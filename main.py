from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json
import datetime
#import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, JSON, SMALLINT, TEXT, TIME, TIMESTAMP, \
            VARCHAR
from sqlalchemy.orm import sessionmaker
from time import sleep
from bs4 import BeautifulSoup

# init config

WINDOW_SIZE = "1920,1080"

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

driver = webdriver.Chrome(options=chrome_options)  
driver.implicitly_wait(20)

# create sqlite table

Base = declarative_base()

class Location(Base):
    __tablename__ = 'location'
    latitude = Column(TEXT, primary_key=True)
    longitude = Column(TEXT, primary_key=True)
    title = Column(TEXT, nullable=True)
    address = Column(TEXT, nullable=True)
    region = Column(TEXT, nullable=True)

engine = create_engine('sqlite:///mymap.db')
Base.metadata.create_all(engine)

# try:
#     conn = sqlite3.connect('mymap.db')
#     print("Opened database successfully")
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE location
#                 (latitude text, longitude text, title text, address text, region text)''')
#     conn.commit()
#     conn.close()
# except:
#     pass


# get data from html file
soup = BeautifulSoup(open(".\\GoogleBookmarks.html", encoding="utf-8"), "html.parser")

# def insertDataToDB(latitude, longitude, title, address, region):
#     conn = sqlite3.connect('mymap.db')
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO location VALUES ('{}','{}','{}','{}','{}')".format(latitude, longitude, title, address, region))
#     conn.commit()
#     conn.close()

def insertDataToDB(latitude, longitude, title, address, region):
    engine = create_engine('sqlite:///mymap.db')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    try:
        content = {"latitude": latitude , "longitude": longitude, "title": title, "address": address, "region": region}
        data = Location(**content)
        session.add(data)
        session.commit()
    # roll back the execution and raise the error
    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

for location_data in soup.find_all('a'):
    print(location_data["href"])
    print(location_data.text)

for location_data in soup.find_all('a'):
    #title = "Gerry's Grill - Bohol"
    #source_url = "http://maps.google.com/?cid=5329396577834908057"
    title = location_data.text
    source_url = location_data["href"]
    transformed_url = source_url.replace("http", "https").replace("maps", "www").replace("/?", "/maps?")

    driver.get(transformed_url)
    #print(driver.find_element_by_xpath("//*"))

    current_url = driver.current_url
    print(transformed_url)
    print(current_url)
    while(current_url == transformed_url):
        sleep(1)
        print("didn't get real url, sleep 0.5 sec")
        current_url = driver.current_url
    latitude = current_url.split("/@")[1].split("/data")[0].split(",")[0]
    longitude = current_url.split("/@")[1].split("/data")[0].split(",")[1]
    print(latitude, longitude, title)
    address = ""
    region = ""
    try:
        address = driver.find_element_by_xpath('//div[@data-tooltip="複製地址"]').text.rstrip().replace('\n','').replace('\t','')
    except:
        pass
    print(address)
    try:
        region = driver.find_element_by_xpath('//button[@data-tooltip="複製 plus code"]').find_element_by_xpath('./../..').text.rstrip().replace('\n','').replace('\t','')
    except:
        pass
    print(region)

    insertDataToDB(latitude, longitude, title, address, region)
    driver.delete_all_cookies()

    #sleep(5)

driver.close()


