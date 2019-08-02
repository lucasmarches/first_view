import csv
import re
import requests
from bs4 import BeautifulSoup
from datetime import date

#Get the date and save it in a string
date = date.today()
year = str(date.year)
month = str(date.month)
day = str(date.day)
date_string = day + "/" + month + "/" + year

#Where the end content will be stored to go in the csv file
results = []

#Open the file with all the links and save all the information in a list
links = []
links_problem = []
csv_file = open('links_sec_2.csv', 'r', encoding='UTF-8', newline='')
file_reader = csv.reader(csv_file, delimiter=';')
for row in file_reader:
    links.append(row[0].split(";"))

#Iterate through the list with all the published content
for content in links:
    #Only open the link of what contains the word "nomear" which means do give a job to someone and it is not a correction ('retificação' in portuguese)
    if "NOMEAR" in content[3] or "Nomear" in content[3] or "nomear" in content[3]:
        legal_instrument = content[2].split(" ")[0]
        link = content[0]
        if not re.search(r"retificacao", link):
            where = content[1]
            try:
                r = requests.get(link)
            except:
                links_problem.append(link)
                pass
            soup = BeautifulSoup(r.text, "html.parser")
            content = soup.body.find_all("p", class_="dou-paragraph")

            #Save what we want in only one string
            content_clean = []
            for item in content:
                content_clean.append(item.text)
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

                #Only returns if there is content in the appointed
                if len(das_code) > 0 and len(appointed) > 3:
                    results.append([legal_instrument, job_giver, appointed, job, where, das_code[0], date_string, link])

#Save the data in a csv file
file_name = "Nomeacoes/"+ day + "_" + month + "_" + year + "_nomeacoes.csv"

#Writes a csv with the list of links for the first section
file = open(file_name,  "w", encoding='UTF-8', newline='')
writer = csv.writer(file,  delimiter=";")
writer.writerow(["Instrumento_Legal", "Quem_nomeou", "Nomeado", "Trabalho", "Local_trabalho", "DAS", "Data_publicacao", "Link"])
for el in results:
    writer.writerow(el)

print ("Could not open " + str(len(links_problem)) + " links")
print (links_problem)
