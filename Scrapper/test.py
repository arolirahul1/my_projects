from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
l=[]
options = Options()     
#options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(chrome_options=options,executable_path='chromedriver_win32')
driver.get('https://www.naukri.com/jobs-in-india-2?clusters=functionalAreaGid,experience&experience=2&glbl_qcrc=1019')
time.sleep(10)  
"""page = driver.execute_script('return document.body.innerHTML')
soup = BeautifulSoup(page, 'html.parser')"""
elements = driver.find_elements(By.XPATH, '//a[@class="title ellipsis"]')
for element in elements:
    href = element.get_attribute('href')
    l.append(href)
print(l)