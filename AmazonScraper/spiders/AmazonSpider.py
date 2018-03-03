# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from AmazonScraper.items import AmazonscraperItem
from pip._vendor import requests
from threading import Thread
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
import os

class AmazonspiderSpider(scrapy.Spider):
    name = 'AmazonSpider'
    allowed_domains = ['amazon.com.au']
    start_urls = ['https://www.amazon.com.au/gp/search/other/ref=lp_4913311051_sa_p_89?rh=n%3A4851683051%2Cn%3A%214851684051%2Cn%3A4913311051&bbn=4913311051&pickerToList=lbr_brands_browse-bin&ie=UTF8&qid=1520062003']

    