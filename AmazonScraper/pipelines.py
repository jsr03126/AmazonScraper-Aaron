# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy, os
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

class AmazonscraperPipeline(object):
    # def process_item(self, item, spider):
    #     return item
	def get_media_requests(self, item, info):
		print("\n\nGET MEDIA REQUEST RESULTS\n")
		print("self = %s"%self)
		print("item = %s"%item)
		print("info = %s"%info)
		print("\n")
		img_urls = item['image_urls']
		# for img_url in img_urls:
		yield Request(img_urls)

	# the list of tuples received by item_completed() is guaranteed
	# to retain the same order of the requests returned from the 
	# get_media_requests() method
	# "results" is the parameter
	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		print("\n\nITEM COMPLETED RESULTS\n")
		print("self = %s"%self)
		print("results = %s"%results)
		print("item = %s"%item)
		print("info = %s"%info)

		if not image_paths:
			raise DropItem("Item contains no images")
		item['image_paths'] = image_paths
		return item