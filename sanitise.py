# created 03/03/2018
# author jsr03126
# amazon.com.au

import webbrowser ,  sys , csv
from pip._vendor import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import bs4 , requests
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
import random

ROOT    = "https://www.amazon.com.au/gp/site-directory/ref=nav_shopall_btn"
base_url = "https://www.amazon.com.au"
headers = {'Accept':'text/css,*/*;q=0.1',
		'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		'Accept-Encoding':'gzip,deflate,sdch',
		'Accept-Language':'en-US,en;q=0.8',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883 Safari/537.36'}

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]


# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy():
	return random.randint(0, len(proxies) - 1)


def ReplaceSysbols(filename):
		filename = filename.replace('(', '')
		filename = filename.replace(')', '')
		filename = filename.replace(' ', '')
		filename = filename.replace(',', '')
		return filename

def ExtractMainInformation(html):
	# Retrieve latest proxies
	proxies_req = Request('https://www.sslproxies.org/')
	proxies_req.add_header('User-Agent', ua.random)
	proxies_doc = urlopen(proxies_req).read().decode('utf8')

	soup = BeautifulSoup(proxies_doc, 'html.parser')
	proxies_table = soup.find(id='proxylisttable')

	# Save proxies in the array
	for row in proxies_table.tbody.find_all('tr'):
		proxies.append({
			'ip':   row.find_all('td')[0].string,
			'port': row.find_all('td')[1].string
		})

	# Choose a random proxy
	proxy_index = random_proxy()
	proxy = proxies[proxy_index]

	for n in range(1, 100):
		req = Request('http://icanhazip.com')
		req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')

		# Every 5 requests, generate a new proxy
		if n % 5 == 0:
			proxy_index = random_proxy()
			proxy = proxies[proxy_index]

		# Make the call
		try:
			my_ip = urlopen(req).read().decode('utf8')
			print('#' + str(n) + ': ' + my_ip)
			
			list_cateogry         = html.findAll('td')

			for category_td in list_cateogry[1:4]:
				category_div      = category_td.findAll('div')
				category_count    = len(category_div)
				for category in category_div[0:category_count]:
					category_name = category.find('h2').getText(strip=True)
					
					if ((category_name != "Books & Audible") and (category_name != "Music, Movies & Games")):
						# print("---------------------TOP CATEGORY ------------------")
						# print(category_name)
						sub_cat      = category.find('ul').findAll('li')
						sub_count    = len(sub_cat)
						for sub_menu in sub_cat[0:sub_count]:
							sub_category_link = sub_menu.find('a').get('href')
							sub_category_title = sub_menu.find('a').getText(strip=True)
							firsturl = base_url + sub_category_link
							print(sub_category_title)
							print(firsturl)

							try:
								mainresponse  = requests.get(firsturl, headers = headers)
								mainhtml      = BeautifulSoup(mainresponse.content , 'html.parser')
								ExtractSubCategory(mainhtml, sub_category_title , firsturl)
							except Exception as e:
								print("There was first problem : %s" % (e))
								continue
					else:
						continue

		except: # If error, delete this proxy and find another one
			del proxies[proxy_index]
			print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
			proxy_index = random_proxy()
			proxy = proxies[proxy_index]


	
				
def ExtractSubCategory(html, sub_category_title , firsturl):
	uls = html.find('div', attrs = {'id' : "leftNav"}).findAll('ul')
	ul_count = len(uls)
	ul = uls[ul_count - 2].findAll('li')
	count = len(ul)
	real_url = ul[count - 1].find('span').find('a').get('href')
	secondurl = base_url + real_url
	print(secondurl)
	try:
		subresponse   = requests.get(secondurl, headers = headers)
		secondhtml    = BeautifulSoup(subresponse.content , 'html.parser')
		ExtractInformation(secondhtml ,sub_category_title, firsturl)
	except Exception as e:
		print("There was second problem : %s" % (e))
		# continue

def ExtractInformation(html, sub_category_title, firsturl):
	uls = html.find('div', attrs = {'id' : "ref_4910514051"}).findAll('ul')
	ul_count = len(uls)
	total_count = 0
	for ul in uls[0:ul_count]:
		lis = ul.findAll('li')
		li_count = len(lis)
		for li in lis[0:li_count]:
			products = li.findAll('span')
			num = int(ReplaceSysbols(products[2].getText()))
			total_count = total_count + num
	print(total_count)
	writecsv(sub_category_title, firsturl, total_count)


def writecsv(category_title, url, count):
	filename              = 'categories.csv'
	with open(filename, 'a') as outfile:
		writer            = csv.writer(outfile)
		row               = []
		
		row.append(category_title)
		row.append(url)
		row.append(count)
		writer.writerow(row)
		outfile.close()


def main():

	response             =  requests.get(ROOT)
	try:
		response.raise_for_status()
	except Exception as e:
		print("There was a problem : %s" % (e))
	initial              = BeautifulSoup(response.content, 'html.parser')
	ExtractMainInformation(initial)

if __name__ == "__main__":
	main()
