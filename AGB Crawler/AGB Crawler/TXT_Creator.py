import csv
import requests
import itertools

from bs4 import BeautifulSoup as bs


with open("List Generation/new_agb.csv" , newline="") as csv_file:
    list_reader = csv.reader(csv_file, delimiter=",")
    # These variables and islice are just for my convenience to only create a few .txt at a time
    startingPoint = 31
    endPoint = None
    partOfList = itertools.islice(list_reader, startingPoint, endPoint)
    #next(list_reader, None)
    counter = 0
    for row in partOfList:
        if len(row) > 4:
            continue
        if counter == 5:
            break
        print("%s: %s" % (row[1], row[3][:-3]))


        resp = requests.get(row[3][:-3])
        soup = bs(resp.text, features="html.parser")

        # rip it out
        for script in soup(["script", "style"]):
            script.extract()
        # for the rare Case some page doesn't have <body>
        try:
            # get text
            text = soup.body.get_text()
        except AttributeError:
            continue
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        with open("Text Extraction/txt_output/%s.txt" % row[1], "w", encoding='utf-8') as file:
           file.write(text)
           counter += 1