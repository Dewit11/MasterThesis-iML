import os
import csv
import requests
from bs4 import BeautifulSoup as bs

with open("../List Generation/new_agb.csv", newline="") as csv_file:
    list_reader = csv.reader(csv_file, delimiter=",")
    next(list_reader, None)
    counter = 0
    for row in list_reader:
        if len(row) > 4:
            continue
        if counter == 50:
            break

        print("%s: %s" % (row[1], row[3][:-1]))
        print (row[3][:-1])

        resp = requests.get(row[3][:-1],headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        soup = bs(resp.text, features="html5lib")

        with open("%s/html_output/%s.html" % (os.getcwd(), row[1]), "w", encoding='utf-8') as file:
            file.write(soup.prettify())
            counter += 1