# coding : utf-8
# author : jsr03126
# since  : 03/03/2018
# AmazonSpider for All Computers & Accessories

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
	start_urls 		= ['https://www.amazon.com.au/gp/search/other/ref=lp_4851683051_sa_p_6?rh=n%3A4851683051&bbn=4851683051&pickerToList=enc-merchantbin&ie=UTF8&qid=1520177572']

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
		# 	a[count] = temp
		# 	count = count + 1

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

		item = AmazonscraperItem()
		item['name']   = title
		item['vendor'] = response.meta.get('Seller')
		# item['asin']   = asin
		item['price']  = price
		return item
