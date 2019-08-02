import csv
import re
import requests
import timeit
from bs4 import BeautifulSoup

#Start the timer
tic=timeit.default_timer()

def find_result(text):
    #Function to find the result in a Brazilian antitrust decision
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

#Create a list for new operations and another that will store any case not foreseen by the algorithm
others = []
new_ac = []
sg_decisions = []

#Open the file and save all the information in a list
links_1 = []
csv_file_1 = open('links_sec_1.csv', 'r', encoding='UTF-8', newline='')
file_reader_1 = csv.reader(csv_file_1, delimiter=';')
for row in file_reader_1:
    links_1.append(row[0].split(";"))

#FIRST SECTION
#Check to see if it is related to the antitrust body and it is not the ATA from the last public meeting
#If yes, open the link
for ind in range(len(links_1)):
    department_hierarchy = links_1[ind][1].split(">")
    if len(department_hierarchy) > 1 and department_hierarchy[1].strip() == "Conselho Administrativo de Defesa Econômica" and "ATA" not in links_1[ind][2] and "PAUTA" not in links_1[ind][2]:
        link_1 = links_1[ind][0]
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


                    #Print all the information in the case of the search for the companies and the process did not throw an error
                    if companies == "":
                        others.append(dec)
            #Excepetions needed to to inconsistencies in the way the information is published
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

#Open the file and save all the information in a list
links_3 = []
csv_file_3 = open('links_sec_3.csv', 'r', encoding='UTF-8', newline='')
file_reader_3 = csv.reader(csv_file_3, delimiter=';')
for row in file_reader_3:
    links_3.append(row[0].split(";"))

for ind in range(len(links_3)):
    department_hierarchy_3 = links_3[ind][1].split(">")
    if len(department_hierarchy_3) > 1 and department_hierarchy_3[1].strip() == "Conselho Administrativo de Defesa Econômica":
        link_3 = links_3[ind][0]
        print (link_3)
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


#LAST THINGS, PRINTING IT ALL
#The most important first, SG decisions
if len(sg_decisions) > 0:
    print ("Decisões publicadas hoje:")
    print ("")
    for ac in sg_decisions:
        print (ac)
    print ("")

#New cases
if len(new_ac) > 0:
    print ("Novos ACs no Cade:")
    print ("")
    for ac in new_ac:
        print (ac)
    print ("")

#If there is something in others at the end of the analysis, print it
if len(others) >0:
    print ("Outras decisões:")
    print ("")
    for el in others:
        print (el)
        print ("")

#Stop the timer
toc=timeit.default_timer()
#Total time in second
total_time = toc - tic

print ("Done in " + str(total_time/60) + " minutes")
