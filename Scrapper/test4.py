from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
python_count=0
options = Options()
driver = webdriver.Chrome(chrome_options=options,executable_path='chromedriver_win32')
l=[]
m=['https://www.naukri.com/jobs-in-india?clusters=functionalAreaGid,experience&experience=2&glbl_qcrc=1019',
'https://www.naukri.com/jobs-in-india-2?clusters=functionalAreaGid,experience&experience=2&glbl_qcrc=1019']
string_counts = {'Python': 0, 'ML': 0, 'DL': 0, 'MYSQL':0, 'Database':0, 'HTML':0, 'Javascript':0, 'NLP':0, 'CV':0}
class execute:
    def ScrapfromURL(self, link, class_name):
        driver.get(link)
        time.sleep(10)
        return driver.find_elements(By.XPATH, f'//div[@class="{class_name}"]')[0].text

    def countnumberofstrings(self, s):
        s.replace('Machine Learning', 'ML')
        s.replace('machine learning', 'ML')
        s.replace('Deep learning', 'DL')
        s.replace('deep learning', 'DL')
        s.replace('Natural language processing', 'NLP')
        s.replace('computer vision', 'CV')
        python_count=s.count('Python')
        ml_count=s.count('ML')
        dl_count=s.count('DL')
        mysql_count=s.count('MySQL')
        database_count=s.count('Database')
        html_count=s.count('HTML')
        javascript_count=s.count('Javascript')
        NLP_count=s.count('NLP')
        CV_count=s.count('CV')
        return {'Python': python_count, 'ML': ml_count, 'DL': dl_count, 'MYSQL':mysql_count, 'Database':database_count, 'HTML':html_count, 'Javascript':javascript_count, 'NLP':NLP_count, 'CV':CV_count}
    
    def run(self, url):
        
        driver.get(url)
        time.sleep(10)  
        elements = driver.find_elements(By.XPATH, '//a[@class="title ellipsis"]')
        for element in elements:
            href = element.get_attribute('href')
            l.append(href)
        print(l)
        for j in l:
            string=self.ScrapfromURL(j, 'dang-inner-html')
            current_counts = self.countnumberofstrings(string)
            for key, value in current_counts.items():
                if key in string_counts:
                    string_counts[key] += value
                    print(string_counts)
                else:
                    string_counts[key] = value
        l.clear()

execute().run('https://www.naukri.com/jobs-in-india?clusters=functionalAreaGid,experience&experience=2&glbl_qcrc=1019')
print(string_counts)
