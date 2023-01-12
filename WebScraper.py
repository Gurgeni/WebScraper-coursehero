from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import os
import re
import requests
#from seleniumwire import webdriver
from twocaptcha import TwoCaptcha
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

url = 'https://www.coursehero.com/study-guides/'
baseUrl = 'https://www.coursehero.com'
http_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'authority': 'www.coursehero.com',
    'method': 'GET',
    'scheme': 'https',
    'accept-language': 'en-US,en;q=0.5',
    'cache-control': 'max-age=0',
}

APY_KEY = 'FFFFFFFFFFFFFFFFFFFFFFFFF'

solver = TwoCaptcha(APY_KEY)

ERRORIMAGES_FILE = '/ImgErros.txt'
ERRORZIP_FILE='/ErrorZipUrls.txt'
ERRORURL_FILE='/ErrorUrls.txt'

def SolveCaptcha(sieteKey, siteUrl):
    result = solver.recaptcha(sitekey=sieteKey,url=siteUrl)
    print('2CAPTCHA RESULT:')
    print(result)
    return result.get('code')


def MkDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_valid_filename(s):
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def SaveHtml(path, html):
    with open(path+'.html', 'w', encoding="utf-8") as f:
        f.write(html)


def SaveImg(path, img):
    with open(path, 'wb') as f:
        f.write(img)


def SaveErrorUrl(url, topicName):
    data = url+','+topicName
    path = ERRORURL_FILE
    with open(path, 'a') as f:
        f.write(data)
        f.write('\n')

def SaveErrorZipUrl(url, folderPath):
    data = url+','+folderPath
    path = ERRORZIP_FILE
    with open(path, 'a') as f:
        f.write(data)
        f.write('\n')

def SaveErrorImgaes(url, folderPath):
    data = url+','+folderPath
    path = ERRORIMAGES_FILE
    with open(path, 'a') as f:
        f.write(data)
        f.write('\n')


class Topic:
    def __init__(self, link, name):
        self.link = link
        self.name = name


class SubTopic:
    def __init__(self, link, name, module, path):
        self.link = link
        self.name = name
        self.module = module
        self.path = path


def GetAllTopics():
    html = CheckCaptcha(url)
    soup = BeautifulSoup(html, 'html.parser')
    topics = soup.findAll(class_='article')
    counter = 0
    topicsArray = []
    for topic in topics:
        link = topic['href']
        name = topic.get_text()
        realName = ReNameTopic(topicsArray, name)
        print(f'name:{realName},link:{link}')
        topicsArray.append(Topic(link, realName))
        counter += 1
    print(f'Number of Topics:{counter}')
    return topicsArray


def ReNameTopic(topicsArray, name):
    r = re.compile(f'{name}\([0-9]+\)')
    names = [x.name for x in topicsArray]
    newlist = list(filter(r.match, names))
    size = len(newlist)
    if size > 0:
        return f'{name}({size+1})'
    for topic in topicsArray:
        if topic.name == name:
            return f'{name}(1)'
    return name


def GetAllSubTopic(topic):
    subUrl = baseUrl+topic.link
    folder = 'studyguidesff\\' + get_valid_filename(topic.name)
    html = CheckCaptcha(subUrl)
    MkDir(folder)
    soup = BeautifulSoup(html, 'html.parser')
    rowArticles = soup.find(class_='row articles')
    module = ''
    subTopics = []
    counter = 0
    for col in rowArticles.children:
        for article in col.children:
            if article.h2 != None:
                module = article.h2.get_text()
                # print(f'Module Name:{module}')
            elif article.a != None:
                name = article.a.get_text()
                link = article.a['href']
                subTopics.append(SubTopic(link, name, module, folder))
                counter += 1
                # print(f'Module:{module},Name:{name},Link:{link}')
    print(f'Got Subtopic:{counter} in Topic:{topic.name}')
    return subTopics


def FindImgResponse(url,imgRespones):
    if url.startwith('/assets'):
        url = baseUrl+url
    for req in imgRespones:
        if req.url == url:
            return req
    return 0


def fetchPage(subTopic):
    pageUrl = baseUrl+subTopic.link
    ValidTopicName = get_valid_filename(subTopic.name)
    folderPath = subTopic.path + '\\' + \
        get_valid_filename(subTopic.module) + '\\'+ValidTopicName+'\\'
    html = CheckCaptcha(pageUrl)
    MkDir(folderPath)
    SaveHtml(folderPath+ValidTopicName, html)
    return 1


def CheckCaptcha(url):
    while 1:
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        if html.__contains__('Request unsuccessful'):
            print('fetchPage Html contains CAPTCA!!!')
            CapthaClick(url)
            time.sleep(3)
            continue
        return html


def CapthaClick(url):
    try:
        time.sleep(1)
        mainFrame = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(mainFrame)
        el = driver.find_element(By.CLASS_NAME, 'g-recaptcha')
        key = el.get_attribute('data-sitekey')
        print(f'CAPTCHA KEY:{key}')
        el.click()
        time.sleep(1)
        code =SolveCaptcha(key, url)
        ClickSubmit(code)
        return
    except Exception as e:
        print("CAPTCHA CLICK EXCEPTION:")
        print(str(e))


def ClickSubmit(code):
    driver.execute_script("onCaptchaFinished('" + code + "');")

def main():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()    
    topicsArray = GetAllTopics()
    topiccounter = 1
    PageFetched = 1
    for topic in topicsArray:
        subTopics = GetAllSubTopic(topic)
        for subTopic in subTopics:
            fetchPage(subTopic)
            print(f'PageFetched:{PageFetched}')
            PageFetched += 1
        print(f'Topic:{topic.name} Done!!!')
        print(f'TopicCounter:{topiccounter}')
        PageFetched = 1
        topiccounter += 1
        time.sleep(10)
    print('Finished')
    driver.close()


if __name__ == "__main__":
    main()
