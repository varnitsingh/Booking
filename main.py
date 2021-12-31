import time
from Booking.booking import Booking
import csv
import random
import string

if __name__ == '__main__':
    # B = Booking('fsjahgj','postgreSQL')
    # # B.create_database()
    # print(B.count_entries('Hungary'))
    # quit()
    with open('countries.csv','r',encoding='utf-8-sig') as rf:
        reader = csv.reader(rf)
        flag = True
        for i in reader:
            if i[0] == 'Romania':
                flag = False
            if flag:
                continue
            random_string = ''.join(random.choice(string.ascii_uppercase) for i in range(5))
            B = Booking(random_string,'postgreSQL')
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
                

