from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from .models import LinkSection1, LinkSection2, LinkSection3, PublicJobs, CadeCases
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import requests
import os
from rq import Queue
from worker import conn

q = Queue(connection=conn)

#Creates the function that will get the links
def get_links(secao, day, month, year):
    url = "http://www.in.gov.br/leiturajornal?data=" + str(day) + "-" + str(month) + "-" + str(year) + "&secao=do" + str(secao)
    #Open the browser in headless mode and go to the webpage where the scrapping will start
    chrome_options = Options()
    chrome_options.binary_location = "/app/.apt/usr/bin/google-chrome"
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path="/app/.chromedriver/bin/chromedriver", chrome_options=chrome_options)
    driver.get(url)

    #Creates the lists that will be returned in the end
    links_list = []
    department_list = []
    decisions_list = []
    intro_list = []

    #Get the first 10 links and append it to the links list
    links_first_10 = driver.find_elements_by_css_selector('li.materia-link > a')
    dept_first_10 = driver.find_elements_by_css_selector('li.materia-link > a > small')
    dec_first_10 = driver.find_elements_by_css_selector('li.materia-link > a > h6')
    intro_first_10 = driver.find_elements_by_css_selector('li.materia-link > a > p')
    for el in range(0,10):
        links_list.append(links_first_10[el].get_attribute('href'))
        department_list.append(dept_first_10[el].text)
        decisions_list.append(dec_first_10[el].text)
        intro_list.append(intro_first_10[el].text)

    #Click the next button. Because it is the first page, there is only one button with this class
    driver.find_element_by_css_selector('b > span.pagination-button').click()

    #Get the 10 links in the second page
    links_second_10 = driver.find_elements_by_css_selector('li.materia-link > a')
    dept_second_10 = driver.find_elements_by_css_selector('li.materia-link > a > small')
    dec_second_10 = driver.find_elements_by_css_selector('li.materia-link > a > h6')
    intro_second_10 = driver.find_elements_by_css_selector('li.materia-link > a > p')
    for el in range(0,10):
        links_list.append(links_second_10[el].get_attribute('href'))
        department_list.append(dept_second_10[el].text)
        decisions_list.append(dec_second_10[el].text)
        intro_list.append(intro_second_10[el].text)

    #Check if there is a next button. While there is, click on it and copy the links and all the other elements
    buttons = driver.find_elements_by_css_selector('span.pagination-button')
    while len(buttons) == 7:
        buttons[-1].click()
        page_links = driver.find_elements_by_css_selector('li.materia-link > a')
        page_dept = driver.find_elements_by_css_selector('li.materia-link > a > small')
        page_dec = driver.find_elements_by_css_selector('li.materia-link > a > h6')
        page_intro = driver.find_elements_by_css_selector('li.materia-link > a > p')
        #In case of error in the cretion of the scrapped page, it adds elements to the list with content to prevent error of index out of range
        if len(page_intro) < 10:
            errors = 10 - len(page_intro)
            for num in range(errors):
                intro_list.append("Error in the page")
        for el in range(len(page_links)):
            links_list.append(page_links[el].get_attribute('href'))
        for el in range(len(page_dept)):
            department_list.append(page_dept[el].text)
        for el in range(len(page_dec)):
            decisions_list.append(page_dec[el].text)
        for el in range(len(page_intro)):
            #This prevent crashing in case of an error in the creation of the scrapped webpage by ignoring the content in the page
            if len(page_intro) < 10:
                intro_list.append("Error in the page")
            else:
                intro_list.append(page_intro[el].text)
        buttons = driver.find_elements_by_css_selector('span.pagination-button')

    #closes the driver
    driver.close()

    #and returns the file with all the links
    return [links_list, department_list, decisions_list, intro_list]

#Function to analyze and find the result in a Brazilian antitrust decision
def find_result(text):
    #First, not approving an operation
    result = ""
    if "impugnação" in text:
    #If not approving, look for a recommendation and store the result of the check
        if "recomendação" in text:
            recommendation = re.search(r"(?<=recomendação).*(?=.)", dec).group(0)
            result = "Impugnação com recomendação" + recommendation
        else:
            result = "Impugnação sem recomendação"
    #If approving, stores it
    elif "aprovação" in text:
        result = "Aprovação sem restrição"
    #Check to see if it is about thirs parties in the process
    elif "terceiro interessado" in text:
        #If yes, see if the demand was approved or not and print the result
        if "deferimento" in text:
            result = "Aprovado como terceiro interessado"
        elif "indeferimento" in text:
            result = "Não aceito como terceiro interessado"
    #Check to see if the case was declared as a complex
    elif "complexo" in text:
        result ="Declarado como complexo"
    elif "não conhecimento" in text:
        result = "Não conhecido"
    return result

#Creates the function to analyze the antitrust decisions
def cade():
    from datetime import date
    date = date.today()
    #Create the 3 lists that will be returned: decisions, new cases and other cases
    others = []
    new_ac = []
    sg_decisions = []

    section1 = LinkSection1.objects.all()
    section3 = LinkSection3.objects.all()

    #FIRST SECTION
    #Check to see if it is related to the antitrust body and it is not the ATA from the last public meeting
    #If yes and if it fits another set of criteria, open the link
    for element in section1:
        department_hierarchy = element.origin.split(">")
        if len(department_hierarchy) > 1 and department_hierarchy[1].strip() == "Conselho Administrativo de Defesa Econômica" and "ATA" not in element.measure and "PAUTA" not in element.measure:
            link_1 = element.link
            r_1 = requests.get(link_1)
            soup_1 = BeautifulSoup(r_1.text, "html.parser")
            decisions = soup_1.body.find_all("p", class_="dou-paragraph")
            decision = []
            #Check to see if it is the general superintendency of the antitrust body and, if yes, get all the content
            if department_hierarchy[2].strip() == "Superintendência-Geral":
                for dec in decisions:
                    if dec.text != "":
                        decision.append(dec.text)
            #Iterate though the content to find the information
                for dec in decision:
                    result = ""
                    companies = ""
                    if "Ato de Concentração" in dec:
                        if "Requerentes" in dec:
                            companies = re.search(r"(?<=Requerentes: ).*?(?=Advogad)", dec, re.S)
                            process_number = re.search(r"[0-9]{5}.[0-9]{6}.[0-9]{4}.[0-9]{2}", dec)
                        else:
                            companies = re.search(r"(?<=[0-9]{5}.[0-9]{6}.[0-9]{4}.[0-9]{2}).*?(?=Advogad).*?(?=Advogad)", dec, re.S)
                            process_number = re.search(r"[0-9]{5}.[0-9]{6}.[0-9]{4}.[0-9]{2}", dec)
                        #Test to see if the search was fruitful without throwing an error in case it wasn't
                        try:
                            companies = companies.group(0)
                        except:
                            companies = ""
                        try:
                            process_number = process_number.group(0)
                        except:
                            process_number = ""

                        result = find_result(dec)

                        #Solve the problem when the information is published in different paragraphs, as it happens sometimes
                        if result == "":
                            dec_adjusted =  dec + decision[decision.index(dec)+1]
                            decision[decision.index(dec)+1] = ""
                            result = find_result(dec_adjusted)
                        sg_decisions.append([companies, process_number, result])


                        #Save all the information in the case of the search for the companies and the process did not throw an error
                        if companies == "":
                            others.append(dec)
                #Excepetions needed to deal with inconsistencies in the way the information is published
                    elif dec == "Decido pela aprovação sem restrições." or dec == "Decido pela aprovação sem restrições":
                        pass
                    else:
                        others.append(dec)
            #If it is not the general superintendency, add it to others
            else:
                for dec in decisions:
                    if dec.text != "":
                        others.append(dec.text)

    #SECTION 3
    #Iterate through all the section 3 information to find what realtes to the antitrust agency
    for element in section3:
        department_hierarchy_3 = element.origin.split(">")
        if len(department_hierarchy_3) > 1 and department_hierarchy_3[1].strip() == "Conselho Administrativo de Defesa Econômica":
            link_3 = element.link
            r_3 = requests.get(link_3)
            soup_3 = BeautifulSoup(r_3.text, "html.parser")
            decisions_3 = soup_3.body.find_all("p", class_="dou-paragraph")
            type_pub = soup_3.body.find("p", class_="identifica")
            type_pub = type_pub.text
            #Check to see if it is the general superintendency of the antitrust body
            if len(department_hierarchy_3) > 2:
                if department_hierarchy_3[2].strip() == "Superintendência-Geral":
                    for dec in decisions_3:
                        #Check if it is a new aquisition process and if it is not a correction in an older publication
                        if "Ato de Concentração" in dec.text and type_pub != "RETIFICAÇÃO":
                            process_number = re.search(r"[0-9]{5}.[0-9]{6}.[0-9]{4}.[0-9]{2}", dec.text)
                            companies = re.search(r"(?<=Requerentes: ).*?(?=Advogad)", dec.text, re.S)
                            operation = re.search(r"(?<=operação: ).*(?= Setor)", dec.text)
                            try:
                                new_ac.append([process_number.group(0), companies.group(0), operation.group(0)])
                            except:
                                pass
            else:
                others.append(decisions_3)

    #Save the informations in the Cade cases databases if it is not already there
    for el in new_ac:
        try:
            CadeCases.objects.get(process_number=el[0])
            pass
        except ObjectDoesNotExist:
            instance = CadeCases.objects.create(process_number=el[0], companies = el[1], operation = el[2], date = date)
            instance.save()

    return [sg_decisions, new_ac, others]

#Function to analyze the most important decisions
def important_decisions():
    #This lists will be returned with all the content
    links_emergencial_dec = []
    links_presidency = []
    links_economy = []
    links_other = []
    #Iterate through all the decision to see if it comes from the areas that deserves more attention and save it
    section1 = LinkSection1.objects.all()
    for element in section1:
        ministry = element.origin.split(">")
        #First, check if it comes from the presidency
        if ministry[0] == "Atos do Poder Executivo":
            mp = element.measure.split("Nº")[0]
            if mp == "MEDIDA PROVISÓRIA ":
                links_emergencial_dec.append([element.origin, element.intro, element.link])
            else:
                links_presidency.append([element.origin, element.intro, element.link])
        elif ministry[0] == "Presidência da República " and ministry[1] == " Despachos do Presidente da República":
            links_presidency.append([element.origin, element.intro, element.link])
        elif ministry[0] == "Ministério da Economia ":
            if ministry[1] == " Gabinete do Ministro":
                links_economy.append([element.origin, element.intro, element.link])
        else:
            dec_splitted = element.measure.split(" ")
            if dec_splitted[0] == "DECRETO":
                links_other.append([element.origin, element.intro, element.link])
    return ([links_emergencial_dec, links_presidency, links_economy, links_other])

#Function to save in the database the name of the public jobs nominations
def section2():
    from datetime import date
    date = date.today()
    #Where the end content will be stored to go in the model
    results = []
    links_problem = []
    #Iterate through the list with all the published content
    section2 = LinkSection2.objects.all()
    for content in section2:
        #Only open the link of what contains the word "nomear" which means do give a job to someone
        if "NOMEAR" in content.intro or "Nomear" in content.intro or "nomear" in content.intro:
            legal_instrument = content.measure.split(" ")[0]
            link = content.link
            if not re.search(r"retificacao", link):
                where = content.origin
                try:
                    r = requests.get(link)
                except:
                    links_problem.append(link)
                    pass
                soup = BeautifulSoup(r.text, "html.parser")
                information = soup.body.find_all("p", class_="dou-paragraph")

                #Save what we want in only one string
                content_clean = []
                for item in information:
                    content_clean.append(item.text)
                #Avoid bug when the page load but without any information
                if len(content_clean) == 0:
                    content_clean.append("a")
                #To get who gave the job to the person. It is always the first element in upper cases except when the first element is an empty string
                if content_clean[0] != "":
                    job_giver = re.findall(r"([A-ZÀ-Ü]{2,})", content_clean[0], re.S)
                    job_giver = " ".join(job_giver)
                else:
                    job_giver = re.findall(r"([A-ZÀ-Ü]{2,})", content_clean[1], re.S)
                    job_giver = " ".join(job_giver)

                #To get the name, check to see if the code DAS is in the text because it is always in the same text as the name of the person
                for item in content_clean:
                    #Get the name of the person appointed for a public job and the public job
                    das_code = ""
                    if "DAS" in item:
                        appointed = re.findall(r"([A-ZÀ-Ü]{2,})", item, re.S)
                        das_code = re.findall(r"(?<=cargo ).*?([0-9]{3}.[0-9]{1})", item, re.S)
                        if len(das_code) < 1:
                            das_code = re.findall(r"([0-9]{3}\.[0-9]{1})", item, re.S)
                        job = re.findall(r"(?<=cargo ).*", item, re.S)
                        #Remove only when it is at the end because it can be part of a full name in Brazil, but never as the last component
                        if appointed[-1] == "DAS":
                            appointed = appointed[0:-1]
                        #Remove some common words that are in upper cases
                        if "CPF" in appointed:
                            appointed.remove("CPF")
                        if "SIAPE" in appointed:
                            appointed.remove("SIAPE")
                        if "DOU" in appointed:
                            appointed.remove("DOU")
                        if "SEI" in appointed:
                            appointed.remove("SEI")
                        if "CNEN" in appointed:
                            appointed.remove("CNEN")
                        if "IFE" in appointed:
                            appointed.remove("IFE")
                        if "ASSESSOR" in appointed:
                            appointed.remove("ASSESSOR")
                        if "ASSISTENTE" in appointed:
                            appointed.remove("ASSISTENTE")
                        #Find the name of the appointed is not in upper cases
                        if len(appointed) < 1:
                            appointed = re.findall(r"(?<=servidor. ).*?(?=,)", item, re.S)
                        if len(appointed) > 0:
                            if appointed[-1] == "DAS":
                                appointed = appointed[0:-1]
                            #Repeat it because sometimes you have two times this word in the selection.
                            if appointed[0] == "NOMEAR":
                                appointed = appointed[1:]
                            #Avoid bug when decisions of firing people are published with the replacement
                            if appointed[0] == "EXONERAR":
                                appointed = ""

                        appointed = " ".join(appointed)

                    else:
                        appointed = ""

                    #Only appends if there is content in the appointed
                    if len(das_code) > 0 and len(appointed) > 3:
                        results.append([legal_instrument, job_giver, appointed, job, where, das_code[0],link, date])
    #Save the data in a model
    for el in results:
        instance = PublicJobs.objects.create(legal_intrument=el[0], job_giver = el[1], appointed = el[2], job = el[3], where = el[4], das_code = el[5], link = el[6], date = el[7])
        instance.save()


def links_all(request):
    from datetime import date

    #Delete all the records in the database to make sure the app is not acessing links from previous days
    LinkSection1.objects.all().delete()
    LinkSection2.objects.all().delete()
    LinkSection3.objects.all().delete()

    #Get the day, necessary for the url where the information is
    date = date.today()
    year = date.year
    month = date.month
    day = date.day

    #Call the function and save the information in the database
    for num in range(1,4):
        result = q.enqueue(get_links, num, day, month, year)
        for el in range(0,len(content[0])):
            if num == 1:
                instance = LinkSection1.objects.create(link=content[0][el], origin = content[1][el], measure = content[2][el], intro = content[3][el])
            elif num == 2:
                instance = LinkSection2.objects.create(link=content[0][el], origin = content[1][el], measure = content[2][el], intro = content[3][el])
            elif num == 3:
                instance = LinkSection3.objects.create(link=content[0][el], origin = content[1][el], measure = content[2][el], intro = content[3][el])
            instance.save()

    #Call the antitrust function that will return a list containing three lists
    cade_info = cade()
    #Call the important decisions function that will return a list of four lists
    imp_decisions_info = important_decisions()
    #Call section2 to offer the dowload file with the new jobs
    section2()

    #Creates the context that will contain all the information gathered by the algorithm to be displayed in the page
    context = {
    'cade': cade_info,
    'imp_decisions': imp_decisions_info
    }

    #Return the updated template
    return render(request,'after_third.html', context=context)

class PublicJobsView(generic.ListView):
    model = PublicJobs
    paginate_by = 10

class CadeCasesView(generic.ListView):
    model = CadeCases
    paginate_by = 10
