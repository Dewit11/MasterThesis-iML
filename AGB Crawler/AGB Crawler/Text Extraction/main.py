import os
import csv
import requests


from bs4 import BeautifulSoup as bs


with open("%s/agb_complete.csv" % (os.getcwd()), newline="") as csv_file:
    list_reader = csv.reader(csv_file, delimiter=",")
    next(list_reader, None)
    counter = 0
    for row in list_reader:
        if len(row) > 4:
            continue
        if counter == 50:
            break

        print("%s: %s" % (row[1], row[3]))

        resp = requests.get(row[3])
        soup = bs(resp.text, features="html.parser")

        with open("%s/output2/%s.html" % (os.getcwd(), row[1]), "w") as file:
            file.write(soup.prettify())
            counter += 1