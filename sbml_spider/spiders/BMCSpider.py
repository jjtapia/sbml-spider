# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 14:06:09 2013

@author: proto
"""

import json
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import  CrawlSpider,Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from sbml_spider.items import SbmlSpiderItem
import random
import urlparse
import cPickle as pickle
class BMCSpider(CrawlSpider):
    name = 'bmc'
    
    def __init__(self, start_urls=[], output='.',*args, **kwargs):
        super(BMCSpider, self).__init__(*args, **kwargs)
        with open('results.json') as f:    
            tmp = json.load(f)
        self.urls = [x['Url'] for x in tmp]
        self.allowed_domains = ['http://www.biomedcentral.com/']
        self.deny_domains= ["www.youtube.com","www.facebook.com",
                            "www.reddit.com","www.twitter.com","www.ebay.com","pages.ebay.com",
                            "www.today.com","www.google.com","www.bing.com","www.yahoo.com",
                            "www.apple.com","www.microsoft.com","twitter.com","windows.microsoft.com"]
        self.deny= ["youtube","facebook","reddit","twitter","ebay","today","www.google.com","bing","yahoo",
                    "apple","microsoft","twitter","flickr","digg","deviantart","tumblr","slashdot",
                    "linkedin","sony","playstation","amazon","instagram"  ]
        self.counter = 0
        self.totalCounter = 0
        self.counterArray = set([])
        self.jumps = 0
        self.maxJumps = 1000000
        self.alreadyVisited = []
        rint = random.randint(0,len(self.urls)-1)
        #print self.urls[rint]
        #self.start_urls = [self.urls[rint]]
        #print start_urls
        
        self.start_urls = [start_urls]
        #self.start_urls=['http://www.plosone.org/search/simple?from=globalSimpleSearch&filterJournals=PLoSONE&query=sbml+xml&x=-1243&y=-99&pageSize=1000']        
        self.outputDir = output
        print self.outputDir
        self.rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(SgmlLinkExtractor(allow=('\.xml', )),callback='parseXML'),
        Rule(SgmlLinkExtractor(),follow=True,callback='parse')
            
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
    )

    
    def parse(self,response):
        hxs = HtmlXPathSelector(response)
        self.totalCounter += 1
        with open('{0}/stats.dump'.format(self.outputDir),'wb') as f:
            pickle.dump(self.totalCounter,f)

        for url in hxs.select('//a/@href').extract():
            if '<sbml>' in url:
                yield self.parseXML(response)
            if '.xml' in url:
                yield Request(url,callback=self.parseXML)
            elif ('/article/info' in url) and url not in self.alreadyVisited and 'image' not in url and 'powerpoint' not in url:
            
                self.alreadyVisited.append(url)
                link = urlparse.urljoin(response.url,url)
#            len([x for x in self.deny if x in str(url)]) == 0:
                #print len(self.alreadyVisited),link
                
                yield Request(link, callback=self.parse)
            elif ('/article/fetchSingleRepresentation' in url and '.s0' in url) and 'SBML' in hxs.extract() and 'XML' in hxs.extract():
                link = urlparse.urljoin(response.url,url)
                #from scrapy.shell import inspect_response
                #inspect_response(response)
                
                if 'XML)</p>' in hxs.extract():
                    listOfStrings = hxs.select('//ul[@id="subject-area-sidebar-list"]//div/text()').extract()
                    listOfStrings = tuple(listOfStrings)
                    self.counterArray.add(listOfStrings)
                    with open('{0}/counterArray.dump'.format(self.outputDir),'wb') as f:
                        pickle.dump(self.counterArray,f)
                        
                    
                    
                #print len(self.alreadyVisited),link

                yield Request(link, callback=self.parseXML)
    

    def parseXML(self,response):
        hxs = HtmlXPathSelector(response)
        self.totalCounter += 1
        with open('stats.dump','wb') as f:
            pickle.dump(self.totalCounter,f)

        if 'sbml' in hxs.extract():
            fileName = response.url.split("/")[-1].split('.')[-2]
            print fileName
            self.counter += 1
            #from scrapy.shell import inspect_response
            #inspect_response(response)

            with open('stats.dump','wb') as f:
                pickle.dump(self.totalCounter,f)

            f =  open('{2}/results_{0}_{1}.xml'.format(fileName,self.counter,self.outputDir),'w')
            f.write(hxs.extract())
            f.flush()
            f.close()
            