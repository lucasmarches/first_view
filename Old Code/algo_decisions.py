import csv
import timeit

#Start the timer
tic=timeit.default_timer()

#Save all the information in the file in a list
info = []
csv_file = open('links_sec_1.csv', 'r', encoding='UTF-8', newline='')
file_reader = csv.reader(csv_file, delimiter=';')
for row in file_reader:
    info.append(row[0].split(";"))

links_emergencial_dec = []
links_presidency = []
links_economy = []
links_other = []
#Iterate through all the decision to see if it comes from the areas that deserves more attention and save it
for decision in info:
    ministry = decision[1].split(">")
    #First, check if it comes from the presidency
    if ministry[0] == "Atos do Poder Executivo":
        mp = decision[2].split("Nº")[0]
        if mp == "MEDIDA PROVISÓRIA ":
            links_emergencial_dec.append(decision)
        else:
            links_presidency.append(decision)
    elif ministry[0] == "Presidência da República " and ministry[1] == " Despachos do Presidente da República":
        links_presidency.append(decision)
    elif ministry[0] == "Ministério da Economia ":
        if ministry[1] == " Gabinete do Ministro":
            links_economy.append(decision)
    else:
        dec_splitted = decision[2].split(" ")
        if dec_splitted[0] == "DECRETO":
            links_other.append(decision)

#Prints the results for emergential measuers in a human readable form
if len(links_presidency) > 0:
    print ("Emergential measures published today:")
    print ("")

for content in links_emergencial_dec:
    print (content[1])
    print ("")
    print (content[3])
    print ("")
    print (content[0])
    print ("")

#Prints the results for the presidency in a human readable form
if len(links_presidency) > 0:
    print ("Decisions made by the presidency:")
    print ("")

for content in links_presidency:
    print (content[1])
    print ("")
    print (content[3])
    print ("")
    print (content[0])
    print ("")

#Prints the results for the economy in a human readable form
if len(links_economy) > 0:
    print ("Decisions made by the Economy Ministry:")
    print ("")

for content in links_economy:
    print (content[1])
    print ("")
    print (content[3])
    print ("")
    print (content[0])
    print ("")

#Prints the results for other decrees in a human readable form
if len(links_other) > 0:
    print ("Decisions made by other members of the government:")
    print ("")

for content in links_other:
    print (content[1])
    print ("")
    print (content[3])
    print ("")
    print (content[0])
    print ("")


#Stop the timer
toc=timeit.default_timer()
#Total time in second
total_time = toc - tic

print ("Done in " + str(total_time/60) + " minutes")
