from selenium import webdriver
from selenium.webdriver.common.by import By
import time
python_count=0
driver = webdriver.Chrome(executable_path='chromedriver_win32')
l=[]
m=['https://www.naukri.com/jobs-in-india?clusters=functionalAreaGid,experience&experience=2&glbl_qcrc=1019',
'https://www.naukri.com/jobs-in-india-2?clusters=functionalAreaGid,experience&experience=2&glbl_qcrc=1019']
string_counts = {}
class execute:
    def ScrapfromURL(self, link, class_name):
        driver.get(link)
        time.sleep(10)
        return driver.find_elements(By.XPATH, f'//div[@class="{class_name}"]')[0].text

    def countnumberofstrings(self, s, listofkeywords):
        for i in listofkeywords:
            if i in string_counts:
                string_counts[i]+=s.count(i)
            else:
                string_counts[i]=s.count(i)

    def run(self, i):
        driver.get(i)
        time.sleep(10)  
        elements = driver.find_elements(By.XPATH, '//a[@class="title ellipsis"]')
        for element in elements:
            href = element.get_attribute('href')
            l.append(href)
        print(l)
        for j in range(2):
            string=self.ScrapfromURL(l[j], 'dang-inner-html')
            self.countnumberofstrings(string, ['Python', 'ML', 'Tableau', 'Data Science', 'NLP', 'PowerPoint'])
        l.clear()

if __name__=="__main__":        
    for i in m:
        execute().run(i)
    print(string_counts)