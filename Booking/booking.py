import logging
from logging import handlers
from re import T
import sys
import time
import json
import csv
import requests
from dataclasses import asdict, astuple
import sqlite3
import pycountry
import psycopg2
from bs4 import BeautifulSoup
from lxml import etree
import random
import string

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import options
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, RemoteDriverServerException

from Booking.schema import Hotel
from Booking.urls import URLS
from Booking.xpaths import XPATHS


class Booking:
    def __init__(self,logger_name,database) -> None:
        # Logger stuff
        self.log = logging.getLogger(f"my_logger{logger_name}")
        self.log.setLevel(logging.INFO)
        format = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s")

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(format)

        fh = handlers.RotatingFileHandler('progress.log')
        fh.setFormatter(format)
        fh.setLevel(logging.WARNING)

        self.log.addHandler(fh)
        self.log.addHandler(ch)

        # Driver
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options, executable_path='./geckodriver')
        self.driver.maximize_window()

        # options = Options()
        # options.headless = False
        # options.binary_location = '/var/lib/snapd/snap/bin/chromium'
        # self.driver = webdriver.Chrome('./chromedriver',options=options)
        # self.driver.maximize_window()

        # db
        self.database = database
        if database == 'postgreSQL':
            self.con = psycopg2.connect(
            user = 'doadmin',
            password = 'sMCXjj4BuzaN3fQA',
            host = 'hotels-do-user-9945610-0.b.db.ondigitalocean.com',
            port = 25060,
            database = 'defaultdb',
            sslmode='require')

            self.cur = self.con.cursor()
        else:
            self.con = sqlite3.connect('database/hotels.db')
            self.cur = self.con.cursor()
        # self.save_progress({'index':0})

    def __del__(self):
        try:
            self.driver.close()
        except:
            pass
        try:
            self.con.close()
        except:
            pass

    def save_to_csv(self):
        self.cur.execute("select * from hotels")
        rows = self.cur.fetchall()
        print(len(rows))
        # with open('hotels.csv','w',encoding='utf-8-sig') as wf:
        #     writer = csv.writer(wf)
        #     writer.writerows(rows)

    def create_database(self):
        # self.cur.execute('''CREATE TABLE hotel_links
        #        (url text primary key not null, price text,country text)''')
        # self.cur.execute('delete from links')
        # self.cur.execute("Drop table hotels")
        # self.con.commit()
        # self.cur.execute('''CREATE TABLE hotels
        #        (hotel_name text,address text, country text, phone text, email text, website text, room_types text, 
        #        room_pricing real, features text, facilities text, description text, rating integer, 
        #        review_score float, policies text, place_of_interest_nearby text, transport_nearby text, 
        #        attractions_nearby text,url text primary key not null)''')
        # self.con.commit()
        self.cur.execute('Create table images (filename text primary key not null, url text)')
        self.con.commit()

    def save_into_db(self, row: tuple):
        if self.database == 'postgreSQL':
            try:
                self.cur.execute("Insert into hotel_links values (%s,%s,%s)", row)
                self.con.commit()
            except Exception as e:
                # self.log.info(e)
                self.con.rollback()
                pass
        else:
            try:
                self.cur.execute("Insert into hotel_links values (?,?,?)", row)
                self.con.commit()
            except Exception as e:
                # self.log.info(e)
                pass

    def save_hotel_into_db(self,row:tuple):
        if self.database == 'postgreSQL':
            try:
                self.cur.execute("Insert into hotels values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", row)
                self.con.commit()
            except Exception as e:
                self.log.info(e)
                self.con.rollback()
                pass
        else:
            try:
                self.cur.execute("Insert into hotels values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
                self.con.commit()
            except Exception as e:
                self.log.info(e)
                pass
        
    def save_image_into_db(self,row:tuple):
        try:
            self.cur.execute("Insert into images values (%s,%s,%s)",row)
            self.con.commit()
            return True
        except Exception as e:
            self.log.info(e)
            self.con.rollback()
            return False
        
    def save_images(self,url:str):
        images = []
        self.driver.find_elements(By.XPATH, XPATHS['images'])
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['images']))):
            link = self.driver.find_element(
                By.XPATH, f"({XPATHS['images']})[{i+1}]").get_attribute("href")
            print('.',end='')
            images.append(link)

        print()

        self.log.info(f"Saving {len(images)} images.")

        for image in images[:20]:
            filename = image.split('?')[0].split('/')[-1]
            while True:
                if self.save_image_into_db((filename,url,image)):
                    break
                else:
                    filename = ''.join(random.choice(string.ascii_lowercase) for i in range(7)) + '.jpg'
            # img_data = requests.get(image).content
            # with open('images/'+filename, 'wb') as handler:
            #     handler.write(img_data)

    def parse_hotel(self, url, room_price,country) -> Hotel:
        self.driver.get(url)
        # time.sleep(3)
        # time.sleep(7)
        H = Hotel()
        H.room_pricing = room_price
        H.country = country
        H.url = url
        H.hotel_name = self.driver.find_element(
            By.XPATH, XPATHS['hotel_name']).text.strip()
        H.address = self.driver.find_element(
            By.XPATH, XPATHS['address']).text.strip()
        H.room_types = ''
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['room_types']))):
            H.room_types += self.driver.find_element(
                By.XPATH, f"({XPATHS['room_types']})[{i+1}]").text.strip() + ', '

        H.features = ''
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['features']))):
            H.features += self.driver.find_element(
                By.XPATH, f"({XPATHS['features']})[{i+1}]").text.strip() + ', '

        H.facilities = ''
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['facilities']))):
            H.facilities += self.driver.find_element(
                By.XPATH, f"({XPATHS['facilities']})[{i+1}]").text.strip() + ', '

        H.transport_nearby = ''
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['transport_nearby']))):
            H.transport_nearby += self.driver.find_element(
                By.XPATH, f"({XPATHS['transport_nearby']})[{i+1}]").text.strip() + ', '

        H.place_of_interest_nearby = ''
        H.attractions_nearby = ''
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['nearby_places']))):
            try:
                category = self.driver.find_element(By.XPATH,
                                                    f"{XPATHS['nearby_places']}[{i+1}]/div/span").text.strip().lower()
                if category == "What's nearby".lower():
                    for j in range(len(self.driver.find_elements(By.XPATH, f"{XPATHS['nearby_places']}[{i+1}]/ul/li"))):
                        H.place_of_interest_nearby += self.driver.find_element(
                            By.XPATH, f"({XPATHS['nearby_places']})[{i+1}]/ul/li[{j+1}]").text.strip() + ', '
                elif category == "Top attractions".lower():
                    for j in range(len(self.driver.find_elements(By.XPATH, f"{XPATHS['nearby_places']}[{i+1}]/ul/li"))):
                        H.attractions_nearby += self.driver.find_element(
                            By.XPATH, f"({XPATHS['nearby_places']})[{i+1}]/ul/li[{j+1}]").text.strip() + ', '
            except Exception as e:
                pass
                # self.log.warning("Error in picking nearby attractions.")
                # self.log.warning(e)

        try:
            H.description = self.driver.find_element(
                By.XPATH, XPATHS['description']).text.strip()
        except:
            try:
                H.description = self.driver.find_element(
                    By.XPATH, XPATHS['description2']).text.strip()
            except:
                H.description = None
        H.rating = len(self.driver.find_elements(By.XPATH, XPATHS['rating']))
        try:
            H.review_score = float(self.driver.find_element(
                By.XPATH, XPATHS['review_score']).text.strip())
        except:
            H.review_score = None
        H.policies = self.driver.find_element(
            By.XPATH, XPATHS['policies']).text.strip()

        H.phone = None
        H.email = None
        H.website = None

        # Doing image stuff
        # try:
        #     self.save_images(url)
        # except:
        #     self.log.warning("Error occured while saving images.")
        

        return H
        # with open('data.json','w',encoding='utf-8-sig') as wf:
        #     json.dump(asdict(H),wf,indent=4)

    def query_hotels(self,country):
        con = sqlite3.connect('database/hotels.db')
        cur = con.cursor()
        try:
            cur.execute(f"select * from hotel_links where country='{country}'")
        except:
            self.log.warning(country)
        data = {}
        try:
            with open(f'database/{country}.json','r') as rf:
                data = json.load(rf)
        except:
            pass
        try:
            start = data[country] + 1
        except:
            start = 0
        rows = cur.fetchall()
        length = len(rows)
        for i in range(start,length):
            self.log.info(f"[{country}]{i}/{length}")
            row = rows[i]
            url = row[0]
            price = round(float(row[1].split(' ')[1].replace(',',''))/7,2)
            try:
                H = self.parse_hotel(url,price,country)
                self.save_hotel_into_db(astuple(H))
            except:
                self.log.info("Sleeping for 60 seconds. Parse error.")
                time.sleep(60)
            data[country] = i
            with open(f'database/{country}.json','w') as wf:
                json.dump(data,wf,indent=4)
        con.close()


    def save_hotel_links(self,country):
        # urls = {}
        # try:
        #     with open('urls.json', 'r', encoding='utf-8-sig') as rf:
        #         urls = json.load(rf)
        # except:
        #     pass

        try:
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, XPATHS['main_table'])))
        except:
            pass
        for i in range(len(self.driver.find_elements(By.XPATH, XPATHS['hotel_link']))):
            try:
                hotel_url = self.driver.find_element(
                    By.XPATH, f"({XPATHS['hotel_link']})[{i+1}]").get_attribute("href").split('?')[0]
                room_price = self.driver.find_element(
                    By.XPATH, f"({XPATHS['room_price']})[{i+1}]").text.strip()
                # urls[hotel_url] = room_price
                self.save_into_db((hotel_url, room_price,country))
            except:
                pass

        # with open('urls.json', 'w', encoding='utf-8-sig') as wf:
        #     json.dump(urls, wf, indent=4)

    def navigate_to_locations(self,country):
        count = 1
        while True:
            self.log.info(f"Page: {count}")
            try:
                self.save_hotel_links(country)
            except Exception as e:
                self.log.warning(e)
                self.log.warning("Error occured during save_hotel_links.")
            count += 1
            try:
                if self.driver.find_element(By.XPATH, XPATHS['last_page']):
                    break
            except NoSuchElementException:
                pass
            try:
                self.driver.find_element(By.XPATH, XPATHS['next_page']).click()
                time.sleep(5)
            except:
                self.log.warning("Couldn't click next page.")
                # time.sleep(20)
                break

    def save_progress(self,progress:dict):
        with open('progress.json','w') as wf:
            json.dump(progress,wf,indent=4)

    def select_different_options(self, url,count,country):
        # self.log.info("Function started")
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options, executable_path='./geckodriver')
        self.driver.maximize_window()
        self.driver.get(url)
        time.sleep(10)
        if count < 1000:
            self.navigate_to_locations(country)
            return True
        elif count < 6000:
            data_filter_groups = ['uf']
            try:
                element = self.driver.find_element(
                    By.XPATH, "(//div[@data-filters-group='uf'])[1]//button[@class='_4310f7077 _45807dae0 _638b66011 _f7538b398']")
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(10)
            except Exception as e:
                print(e)
                self.log.info('top destinations elem not found')
                return False
        else:  
            data_filter_groups = ['uf','top_destinations','popular', 'health_and_hygiene', 'SustainablePropertyFilter', 'class', 'popular_activities',
                                'any_deal', 'fc', 'ht_beach', 'mealplan', 'privacy_type', 'ht_id',
                                'popular_nearby_landmarks', 'tdb', 'review_score', 'hotelfacility', 'min_bathrooms',
                                'roomfacility', 'chaincode', 'accessible_facilities',
                                'accessible_room_facilities']
        data = {}
        with open('progress.json','r') as rf:
            data = json.load(rf)
        if country in data:
            idx = data[country]['index']
            start = data[country]["value"]
        else:
            idx = 0
            start = 0
        while idx < len(data_filter_groups):
            temp_xpath = f"(//div[@data-filters-group='{data_filter_groups[idx]}'])[1]//input"
            for i in range(start,len(self.driver.find_elements(By.XPATH, temp_xpath))):
                self.log.info(
                    f"[{country}][{data_filter_groups[idx]}]Clicking option: {i+1}")
                element = self.driver.find_element(
                    By.XPATH, f"({temp_xpath})[{i+1}]")
                self.driver.execute_script(
                    "arguments[0].click();", element)
                time.sleep(10)
                try:
                    self.navigate_to_locations(country)
                except:
                    self.log.info("Failed to scrape hotels.")
                self.driver.execute_script(
                    "arguments[0].click();", element)

                data[country] = {
                    "index": idx,
                    "value": i + 1
                }
                self.save_progress(data)
                time.sleep(10)

            idx += 1
            start = 0
            data[country] = {
                'index':idx,
                "value": start
                }
            self.save_progress(data)

        return True

        # temp_xpath = "//div[@class='_962ef834c cbe47aa30e']"
        # stuff = []
        # for i in range(len(self.driver.find_elements(By.XPATH,temp_xpath))):
        #     element = self.driver.find_element(By.XPATH,f"({temp_xpath})[{i+1}]").get_attribute('data-filters-group')
        #     # print(element)
        #     stuff.append(element)
        # print(stuff)

    def generate_country_link(self):
        countries = []
        for country in pycountry.countries:
            if country.name.find(',') != -1:
                countries.append(country.name.split(',')[0])
            else:
                countries.append(country.name)
        
        data = {}
        with open('countries.json','r',encoding='utf-8-sig') as rf:
            data = json.load(rf)
        length = len(countries)
        flag = True
        for i in range(length):
            if countries[i] == 'Saint Vincent and the Grenadines':
                flag = False
            if flag:
                continue
            self.log.info(f"{i+1}/{length} {countries[i]}")
            self.driver.get(URLS['homepage'])
            time.sleep(5)
            try:
                self.driver.find_element(By.XPATH,XPATHS['cancel_button']).click()
                time.sleep(3)
            except:
                pass
            self.driver.find_element(By.XPATH,XPATHS['search_input']).send_keys(countries[i])
            self.log.info('select date')
            time.sleep(15)
            self.driver.find_element(By.XPATH,XPATHS['search_button']).click()
            time.sleep(5)
            url = self.driver.current_url
            properties = self.driver.find_element(By.XPATH,'//h1').text
            data[countries[i]] = {
                'url': url,
                'properties': properties
            }
            with open('countries.json','w',encoding='utf-8-sig') as wf:
                json.dump(data,wf,indent=4)
            
    def check_countries(self):
        data = {}
        headers = ['country,count,url']
        new_data = []
        with open('data.json','r',encoding='utf-8-sig') as rf:
            data = json.load(rf)
        total = 0
        manual = 0
        for key in data.keys():
            properties = data[key]['properties'].split(':')
            # print(properties)
            country = properties[0].strip()
            if key != country:
                # print(key,', ',country)
                # manual += 1
                data[key]['correct'] = 1
                try:
                    count = properties[1].split('properties')[0].strip().replace(',','')
                    try:
                        total += int(count)
                        data[key]['count'] = int(count)
                        new_data.append([key,int(count),data[key]['url']])
                    except:
                        print(country,properties[1].split('properties')[0].strip())
                except:
                    print(key,country)
                    manual+= 1
            else:
                count = properties[1].split('properties')[0].strip().replace(',','')
                try:
                    total += int(count)
                    data[key]['count'] = int(count)
                    new_data.append([key,int(count),data[key]['url']])
                except:
                    print(country,properties[1].split('properties')[0].strip())
        print(total)
        print(manual)

        new_data.sort(key = lambda x: x[1])
        with open('countries.csv','w',encoding='utf-8-sig') as wf:
            writer = csv.writer(wf)
            writer.writerow(headers)
            writer.writerows(new_data)
        # with open('data2.json','w',encoding='utf-8-sig') as wf:
        #     json.dump(data,wf,indent=4)

    def count_entries(self) -> int:
        self.cur.execute(f"select country,count(country) from hotel_links group by country order by count(country)")
        row = self.cur.fetchall()
        for r in row:
            print(r)

    def merge_db(self):
        self.cur.execute(f"select * from links")
        rows = self.cur.fetchall()
        length = len(rows)
        for i in range(length):
            self.log.info(f"{i}/{length}")
            country = rows[i][0].split('/')[4]
            if country == 'us':
                country = 'United States of America'
            elif country == 'in':
                country = 'India'
            else:
                continue
            self.save_into_db((rows[i][0],rows[i][1],country))
