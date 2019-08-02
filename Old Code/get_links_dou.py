from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import date
import csv
import timeit

#Start the timer
tic=timeit.default_timer()

#Creates the function that will get the links
def get_links(secao, day, month, year):
    url = "http://www.in.gov.br/leiturajornal?data=" + str(day) + "-" + str(month) + "-" + str(year) + "&secao=do" + str(secao)
    #Open the browser in headless mode and go to the webpage where the scrapping will start
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
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


#Get the day, necessary for the url if we don't want to hardcode it
date = date.today()
year = date.year
month = date.month
day = date.day

#Call the function and save the return object in a variable for the first section
for num in range(1,4):
    content_csv = get_links(num, day, month, year)
    #Writes a csv with the list of links for the first section
    file = open("links_sec_" + str(num) + ".csv",  "w", encoding='UTF-8', newline='')
    writer = csv.writer(file,  delimiter=";")
    for el in range(0,len(content_csv[0])):
        line = [content_csv[0][el] + ";"  + content_csv[1][el] + ";" + content_csv[2][el] + ";" + content_csv[3][el]]
        writer.writerow(line)
    print ("section " + str(num) + " done")


#Stop the timer
toc=timeit.default_timer()
#Total time in second
total_time = toc - tic
print ("Done in " + str(total_time/60) + " minutes")
