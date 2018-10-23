import requests
from bs4 import BeautifulSoup
import re

#import sys  # import sys package, if not already imported
#reload(sys)
#sys.setdefaultencoding('utf-8')

url = "https://www.idealo.de/preisvergleich/AllePartner/100I27-90.html"
output = []
file = open('updated_agb.csv', 'a')
file.write("id,name,shop_url,agb_url\n")

i = 0

def extract_shop_info(url):
	url = "https://www.idealo.de" + url
	res = requests.get(url)
	soup = BeautifulSoup(res.text, features="html5lib")

	try:
		name = soup.find("td", {"class" : "shop-address"}).get_text(",").split(",")[0].lstrip()

		links = soup.find_all("a", {"class" : "link-3"})
		for x in links:
			if x.get_text().lstrip() == "AGB":
				url = "https://www.idealo.de" + x['href']
				try:
					res = requests.get(url)
				except:
					url = res.url.replace("https:", "http:")
					print (url)
					res = requests.get(url)
				agb_url = res.url
				shop_url = agb_url.split("//")[1].split("/")[0]
				break
		return {'name':name,'agb_url': agb_url, 'shop_url': shop_url}
	except AttributeError:
		return []


while True:
	res = requests.get(url)
	soup = BeautifulSoup(res.text, features="html5lib")

	all_links = soup.findAll("a", {"class" : "link-2"})
	# Trim down to only include actual shop links from each Page
	shop_links = all_links[1:16]
	for link in shop_links:

		result = extract_shop_info(link['href'])
		if len(result) > 0:
			print(result['name'])
			i = i + 1
			file.write(str(i)+","+result['name']+","+result['shop_url']+","+result['agb_url']+"\n")
	
	#next page
	next = soup.find("a", {"class" : "page-next"})
	print(next)
	url = "https://www.idealo.de" + next['href']

