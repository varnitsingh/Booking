import time
from Booking.booking import Booking
import csv
import random
import string
import sys

def query_single_hotels(start_country):
    random_string = ''.join(random.choice(string.ascii_uppercase) for i in range(5))
    B = Booking(random_string,'postgreSQL')
    with open('countries.csv','r',encoding='utf-8-sig') as rf:
        reader = csv.reader(rf)
        flag = True
        for i in reader:
            if i[0] == start_country:
                flag = False
            if flag:
                continue
            try:
                B.query_hotels(i[0])
            except:
                B.log.info("Sleeping for 60 seconds. Main loop error.")
                time.sleep(60)

if __name__ == '__main__':
    # B = Booking('fsjahgj','postgreSQ')
    # B.merge_db()
    # B.save_to_csv()
    # B.create_database()
    # B.query_hotels('Ukraine')
    # print(B.count_entries())
    query_single_hotels(sys.argv[1])
    quit()
    with open('countries.csv','r',encoding='utf-8-sig') as rf:
        reader = csv.reader(rf)
        flag = True
        for i in reader:
            if i[0] == 'Indonesia':
                flag = False
            if flag:
                continue
            random_string = ''.join(random.choice(string.ascii_uppercase) for i in range(5))
            B = Booking(random_string,'postgreSQ')
            B.log.info(i[0])
            while True:
                try:
                    if B.select_different_options(i[2],int(i[1]),i[0]):
                        try:
                            B.driver.close()
                        except:
                            pass
                        break
                    else:
                        B.log.info("Sleeping for 60 seconds.")
                        time.sleep(60)
                except Exception as e:
                    print(e)
                    B.log.info("Sleeping for 60 seconds.")
                    time.sleep(60)
                

