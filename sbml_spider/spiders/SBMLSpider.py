# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 14:36:33 2013

@author: proto
"""
import json
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import  CrawlSpider,Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from sbml_spider.items import SbmlSpiderItem
import random

class SbmlSpider(CrawlSpider):
    name = 'sbml'
    
    def __init__(self, category=None, *args, **kwargs):
        super(SbmlSpider, self).__init__(*args, **kwargs)
        with open('results.json') as f:    
            tmp = json.load(f)
        self.urls = [x['Url'] for x in tmp]
        self.allowed_domains = []
        self.counter = 0
        self.jumps = 0
        self.maxJumps = 1000000
        self.alreadyVisited = []
        rint = random.randint(0,len(self.urls)-1)
        self.start_urls = self.urls[rint]
        self.rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(SgmlLinkExtractor(allow=('\.xml', )),callback='parseXML')
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
    )


    def parse(self,response):
        hxs = HtmlXPathSelector(response)
        for url in hxs.select('//a/@href').extract():
            if '.xml' in url:
                yield Request(url,callback=self.parseXML)
            elif 'http' in url or 'www' in url and url not in self.alreadyVisited:
                #self.alreadyVisited.append(url)
                #print len(self.alreadyVisited),url
                yield Request(url, callback=self.parse)

    def parseXML(self,response):
        hxs = HtmlXPathSelector(response)
        print 'sbml' in hxs.extract_unquoted(),self.counter
        if 'sbml' in hxs.extract_unquoted():
            f =  open('results{0}.xml'.format(random.randint(0,1000000)),'w')
            f.write(hxs.extract_unquoted())
            f.flush()
            self.counter += 1