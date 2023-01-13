import csv
import os
from urllib.request import Request, urlopen
import pandas as pd
from bs4 import BeautifulSoup
import requests
import smtplib
import ssl
from email.message import EmailMessage
import datetime
from os import rename
from os.path import splitext, exists, join
from shutil import move
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import time
from selenium import webdriver
import re
import smtplib
import dns.resolver
import socket
from dotenv import load_dotenv
load_dotenv()


def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
  
# creates a csv file with the data inputed 


def abstractedReadToDataFrame(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df


def send_email(email_receiver, subject, body, files):
    now = datetime.datetime.now()
    email_sender =  os.getenv('email_sender')
    email_password = os.getenv('email_password')
    em = EmailMessage()
    # em = MIMEMultipart()
    em['From'], em['To'], em['Subject'] = email_sender, email_receiver, subject 
    em.set_content(body)

    for path in files:
        with open(path, 'rb') as file:
            file_data = file.read()
            file_name = file.name.split('/')[-1]
        
        em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
        smtp.quit()

def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name

def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)


def tomide_bs4_make_soup(url, duration, type, scroll):

    soup = []
    option = webdriver.ChromeOptions()
    # option.add_argument("headless")
    # option.add_argument("window-size=1920,1080")
    # option.add_argument("disable-gpu")
    # option.add_argument(" — no-sandbox")
    # option.add_argument(" — disable-dev-shm-usage")
    # options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--incognito")
    # options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36')

    if type == "static":
        req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        return soup

    elif type == "incognito":
        driver = webdriver.Chrome()
        driver.get(url)
        # time.sleep(duration)

        if scroll == True:
            SCROLL_PAUSE_TIME = 10
            last_height = driver.execute_script("return document.body.scrollHeight")   # Get scroll height
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll down to bottom
                time.sleep(SCROLL_PAUSE_TIME)  # Wait to load page
                new_height = driver.execute_script("return document.body.scrollHeight") # Calculate new scroll height and compare with last scroll height
                if new_height == last_height:
                    break
                last_height = new_height
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        return soup

    else: 
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=/Users/tomideisawesome/Library/Application Support/Google/Chrome")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
    return soup

def email_extractor(line):
    return re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', line)


def mail_checker(email): 
    domain_name = email.split('@')[1]
    records = dns.resolver.query(domain_name, 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)
    host = socket.gethostname()
    server = smtplib.SMTP()
    server.set_debuglevel(0)
    server.connect(mxRecord)
    server.helo(host)
    server.mail('me@domain.com')
    code, message = server.rcpt(str(email))
    server.quit()
    if code == 250:
        return email


def emailGenerator(firstname, lastname, company_domain):
    if '/' in company_domain:
        company_domain = company_domain.replace('/', '')
    if 'https:' in company_domain:
        company_domain = company_domain.replace('https:', '')
    if 'http:' in company_domain:
        company_domain = company_domain.replace('http:', '')
    if 'www.' in company_domain:
        company_domain = company_domain.replace('www.', '')

    print ("Generating email list for", firstname, lastname)
    emailList = []

    emailList.append(firstname + "@" + company_domain)
    emailList.append(lastname + "@" + company_domain)

    emailList.append(firstname + lastname + "@" + company_domain)
    emailList.append(lastname + firstname + "@" + company_domain)

    emailList.append(firstname + "." + lastname + "@" + company_domain) # tomide.adeoye@merislabs.com
    emailList.append(lastname + "." + firstname + "@" + company_domain) # adeoye.tomide@merislabs.com

    emailList.append(firstname + lastname[0] + "@" + company_domain) # tomidea@merislabs.com
    emailList.append(lastname[0] + firstname + "@" + company_domain) # atomide@merislabs.com
   
    emailList.append(firstname[0] + lastname + "@" + company_domain) # tadeoye@merislabs.com
    emailList.append(lastname + firstname[0] + "@" + company_domain) # adeoyet@merislabs.com

    emailList.append(firstname + "." + lastname[0] + "@" + company_domain) # tomidea@merislabs.com
    emailList.append(lastname[0] + "." + firstname + "@" + company_domain) # atomide@merislabs.com
   
    emailList.append(firstname[0] + "." + lastname + "@" + company_domain) # tadeoye@merislabs.com
    emailList.append(lastname + "." + firstname[0] + "@" + company_domain) # adeoyet@merislabs.com

    emailList.append(firstname[0] + lastname[0] + "@" + company_domain) # ta@merislabs.com
    emailList.append(lastname[0] + firstname[0] + "@" + company_domain) # ta@merislabs.com
    
    emailList.append(lastname[0] + "." +  firstname[0] + "@" + company_domain) #t.a@meris.com
    emailList.append(firstname[0] + "." +  lastname[0] + "@" + company_domain) #t.a@meris.com
    
    valid = []
    for email in emailList:
        valid.append(mail_checker(email))

    valid = [item for item in valid if item is not None]

    return valid



def google_search(query_for_google):
    search_keys = os.getenv("search_keys").split(",") # an array of search keys
    searchEngineId=  os.getenv("search_engine_id")
    options= {'method' : 'get', 'contentType': 'application/json'}

    for search_key in search_keys:
        google_response  =  requests.get("https://www.googleapis.com/customsearch/v1?key="+search_key+"&q="+query_for_google+"&cx="+searchEngineId, options).json()
        if 'items' in google_response:
            return google_response['items']
        else:
            if google_response['error']['code'] == 429:
                continue
    print("NO KEYS WORKED", google_response['error']['message'])



def txt_db_maker(db, content):
    today = str(datetime.date.today())
    today_2 = f"{today} "
    content = bytes(today_2,'utf-8')
    year_str = str(datetime.datetime.now().year)
    year_edit = bytes(year_str,'utf-8').decode('utf-8')
    date_str = str(datetime.datetime.now().day)
    date_edit = bytes(date_str,'utf-8').decode('utf-8')
    edit = {"1":"01",
            "2":"02",
            "2":"03",
            "4":"04",
            "5":"05",
            "6":"06",
            "7":"07",
            "8":"08",
            "9":"09",}
    try:
        file = open(f"{db}.txt", "x")
        # messenger()
        file.write(today_2)
        file.close()
    except Exception as e:
        file = open(f"{db}.txt", "a+b")
        try:
            try:
                file.seek(-11,2) # seek will not work in negative in text mode, only in byte mode
            except OSError as e:
                print(e)
                # messenger()
                file.write(content)
                file.close()
                os._exit(0)
            year = file.read(10).decode('utf-8')
            file.seek(-11,2)
            date = file.read(10).decode('utf-8')
            if year_edit != year[:4]:
                file.close()
                file = open(f"{db}.txt", "wb")
                file.close()
                file = open(f"{db}.txt", "a+b")
                # messenger()
                file.write(content)
                file.close()
            for x in edit.keys():
                if x == date_edit:
                    date_edit = edit.get(x)
                    break
            if date_edit != date[8:14]:
                # messenger()
                file.write(content)
                file.close()
                os._exit(0)
        except Exception as e:
            print(e)


def create_csv_file(filename, rows): # createCsvFile('scrfabove103.csv', list, header_list)
    pd.DataFrame(rows).to_csv(f"{filename}.csv", mode='a', header=False, index=False)  


# def googleTextToSpeech(text):
#     """Synthesizes speech from the input string of text."""
#     from google.cloud import texttospeech

#     client = texttospeech.TextToSpeechClient()

#     input_text = texttospeech.SynthesisInput(text=text)

#     # Note: the voice can also be specified by name.
#     # Names of voices can be retrieved with client.list_voices().
#     voice = texttospeech.VoiceSelectionParams(
#         language_code="en-US",
#         ss


# from gtts import gTTS
# from playsound import playsound
# text=input("Enter a sentence : ")
# speech=gTTS(text=text,lang="en")        #converting to mp3 in English
# speech.save(r"D:\speech_en.mp3")        #saving the .mp3 file in the given directory
# playsound(r"D:\speech_en.mp3")          #playing the .mp3 file