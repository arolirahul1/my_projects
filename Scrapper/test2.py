from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
l=[]
options = Options()
#options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(chrome_options=options,executable_path='chromedriver_win32')
driver.get('https://www.naukri.com/job-listings-snaplogic-data-science-practitioner-accenture-mumbai-2-to-4-years-261222903293?src=jobsearchDesk&sid=16734374644311810&xp=3&px=2')
time.sleep(10)
#page = driver.execute_script('return document.body.innerHTML')
#soup = BeautifulSoup(page, 'html.parser')
parent = driver.find_elements(By.XPATH, '//div[@class="dang-inner-html"]')[0].text
print(parent)
