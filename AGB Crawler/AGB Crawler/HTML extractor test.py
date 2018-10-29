import csv
import requests

from bs4 import BeautifulSoup as bs


with open("List Generation/new_agb.csv" , newline="") as csv_file:
    list_reader = csv.reader(csv_file, delimiter=",")
    next(list_reader, None)
    counter = 0
    for row in list_reader:
        if len(row) > 4:
            continue
        if counter == 10:
            break

        print("%s: %s" % (row[1], row[3]))

        resp = requests.get(row[3])
        soup = bs(resp.text, features="html.parser")

        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.body.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        with open("Text Extraction/output2/%s.txt" % row[1], "w", encoding='utf-8') as file:
           file.write(text)
           counter += 1