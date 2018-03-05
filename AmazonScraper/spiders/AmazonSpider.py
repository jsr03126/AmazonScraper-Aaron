# coding : utf-8
# author : jsr03126
# since  : 03/03/2018
# github : https://github.com/jsr03126/AmazonScraper-Aaron

import scrapy
from scrapy import Request
from AmazonScraper.items import AmazonscraperItem
from pip._vendor import requests
from threading import Thread
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
import os

class AmazonspiderSpider(scrapy.Spider):
	name			= 'AmazonSpider'
	allowed_domains = ['amazon.com.au']
	start_urls		= ['https://www.amazon.com.au/gp/site-directory/ref=nav_shopall_btn']

	def ReplaceSymbols(self, filename):
		filename 	= filename.replace('\\', '-')
		filename 	= filename.replace('/', '-')
		filename 	= filename.replace(':', '-')
		filename 	= filename.replace('*', '-')
		filename 	= filename.replace('?', '-')
		filename 	= filename.replace('"', '-')
		filename 	= filename.replace('<', '-')
		filename 	= filename.replace('>', '-')
		filename 	= filename.replace('|', '-')
		filename 	= filename.replace('[', '')
		filename 	= filename.replace(']', '')
		return filename

	def parse(self, response):
		categories = response.xpath('.//li')
		cat_count  = len(categories) - 30

		# categories = categories[49:cat_count] # All Amazon Categories

		categories = categories[49:50]   		# All Computers & Accessories
		# categories = categories[50:51]   		# Laptops
		# categories = categories[51:52]   		# Desktops & Monitors
		# categories = categories[52:53]   		# Accessories
		# categories = categories[53:54]   		# Networking
		# categories = categories[54:55]   		# Drives & Storage
		# categories = categories[55:56]   		# Computer Parts & Components
		# categories = categories[56:57]   		# Printers & Ink
		# categories = categories[57:58]   		# Office & School Supplies
		# categories = categories[58:59]   		# All Electronics
		# categories = categories[59:60]   		# Camera & Photo
		# categories = categories[60:61]   		# Home Cinema & Audio
		# categories = categories[61:62]   		# Speakers
		# categories = categories[62:63]   		# Headphones
		# categories = categories[63:64]   		# Wireless Audio
		# categories = categories[64:65]   		# PC & Video Games
		# categories = categories[65:66]   		# Smart Home 						! ERROR !
		# categories = categories[66:67]   		# Wearable Technology
		# categories = categories[67:68]   		# GPS, Navigation & Accessories
		# categories = categories[68:69]   		# Bedding & Linen
		# categories = categories[69:70]   		# Bath & Accessories
		# categories = categories[70:71]   		# Home Décor
		# categories = categories[71:72]   		# Lighting
		# categories = categories[72:73]   		# Storage & Organisation
		# categories = categories[73:74]   		# Household & Cleaning Supplies
		# ............

		for category in categories:
			cat_title   = category.xpath('.//a/text()').extract_first()
			link  		= category.xpath('.//a/@href').extract_first()
			link 		= response.urljoin(link)
			print('\n\nNow ready to enter the category :  %s\n' % cat_title)
			yield Request(link, callback=self.get_cat_page, meta={})

	def get_cat_page(self, response):
		uls 		= response.xpath('.//div[@id="leftNav"]/ul')
		uls_count 	= len(uls)
		ul 			= uls[uls_count - 2 : uls_count - 1]
		for ul in ul:
			li 		= ul.xpath('.//li/span/a/@href').extract_first()
			link 	= li[0:41] + li[61:]
			link  	= response.urljoin(link)
			yield Request(link, callback=self.get_menu_page, meta={})
	
	def get_menu_page(self, response):
		categories  = response.xpath('.//span[@class="pagnLink"]')
		cat_count   = len(categories)/2
		categories  = categories[0:int(cat_count)]
		for category in categories:
			page 	= category.xpath('.//a/@href').extract_first()
			link 	= response.urljoin(page)
			page 	= category.xpath('.//a/text()').extract_first()
			print('\n\nNow ready to enter the category page %s\n' % page)
			yield Request(link, callback=self.get_sellers, meta={'Category' : page})

	def get_sellers(self, response):
		urls 	    = response.xpath('.//span[@class="a-list-item"]')
		for url in urls:
			a_url   = url.xpath('.//a/@href').extract_first()
			a_url   = response.urljoin(a_url)
			category= response.meta.get('Category')
			seller  = url.xpath('.//a/@title').extract_first()
			print('\n\tNow entering into the seller %s\n' % seller)
			yield Request(a_url, callback=self.get_result_page, meta={'Category':category, 'Seller':seller})

	def get_result_page(self, response):
		products 	= response.xpath('//div[@class="s-item-container"]')
		for product in products:
			item 	= product.xpath('.//a/@href').extract_first()
			item 	= response.urljoin(item) 				# Product url
			category= response.meta.get('Category') 	    # Category name
			seller  = response.meta.get('Seller')           # Seller name
			
			yield Request(item, callback=self.get_product_info, meta = {'Category':category, 'Seller':seller})
	
	def get_product_info(self, response):
		title 		= response.xpath('normalize-space(//span[@id="productTitle"])').extract_first()
		title 		= " ".join(title.split())
		price 		= response.xpath('.//span[@id="priceblock_ourprice"]/text()').extract_first()

		print('-------------------------------------')
		print(title)
		print(price)
		print('-------------------------------------')
		# count = 0
		# a = []
		# for temp in response.xpath('.//div[@class="pdTab"]/table/tbody/tr/td/text()').extract():
		# 	print(temp)
			# a[count] = temp
			# count = count + 1

		# count = 0
		# for temp in a:
		# 	# if (temp == 'ASIN'):
		# 	# 	asin = temp[count + 1]
		# 	# 	break
			
		# 	print('-------------------------------------')
		# 	print(count)
		# 	print(temp)
		# 	print('-------------------------------------')
		# 	count = count + 1

		item 			= AmazonscraperItem()
		item['name']    = title
		item['vendor']  = response.meta.get('Seller')
		# item['asin']    = asin
		item['price']   = price
		return item
