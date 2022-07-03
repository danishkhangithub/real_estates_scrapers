# packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import urllib
import datetime
import re


# sold houses class
class soldhouses(scrapy.Spider):
    # scraper name
    name = 'rightmove2'
    # base url
    base_url = 'https://www.rightmove.co.uk/property-for-sale/find.html?'
    # page index
    page_index = 0
    
    current_page = 1

    # string query parameters
    params = {
        'locationIdentifier': '',
        'country': 'england',
        'searchLocation': '',
        'referrer': 'landingPage',

    }

    # headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    }

    # custom setting
    custom_settings = {
    # uncomment to set accordingly
    "CONCURRENT_REQUESTS_PER_DOMAIN":2,
    "DOWNLOAD_TIMEOUT":20  #250 ms  of delay
        }

    # on create
    def __init__(self):

        # inti postcodes
        postcodes = ''

        # open "postcodes.json"
        with open('postcodes.json', 'r') as json_file:
            for line in json_file.read():
                postcodes += line
        # parse postcodes
        self.postcodes = json.loads(postcodes)

    # crawler's entry point
    def start_requests(self):
        # init filename
        filename = './output/Sold_houses_' + datetime.datetime.today().strftime('%Y-%m-%d-%H-%M') + '.jsonl'
        # postcodes count
        count = 0
        self.page_index = 0
        # init string query parameters
        for item in self.postcodes:
            #self.page_index = 0
            self.params['searchLocation'] = item['postcode']
            self.params['locationIdentifier'] = item['locationId']
            #self.params['index'] = self.page_index
            url = self.base_url + urllib.parse.urlencode(self.params) + '&index=' +  str(self.page_index)
            
            yield scrapy.Request(url= url, headers=self.headers,
                                 meta={'postcode': item['postcode'], 'filename': filename, 'count':   count},
                                 callback=self.parse_links)
            break
            count += 1
           

    def parse_links(self, res):

        #         response = Selector(res= text)
        #          with open('res.html', 'w' ) as f:
        #                   f.write(res.text)
        
        postcode = res.meta.get('postcode')
        filename = res.meta.get('filename')
        count = res.meta.get('count')
        
        #         #extract links
        #         for card in res.css('div.propertyCard-content')
        #         #debug selectors
        '''
        content = ''
        with open('res2.html', 'r' ) as f:
             for line in f.read():
                 content += line
        res = Selector(text=content)
        '''
        # extract basic features
        properties = ''.join([script for script in res.css("script::text").getall() if 'window.jsonModel = {"properties":' in script]) 
        properties = json.loads((properties.split('window.jsonModel = ')[-1]).replace(" ", ""))
        properties = properties['properties']
        #print(json.dumps(properties['propertyUrl'],indent = 2))
        #properties = json.dumps(properties['propertyUrl'], indent = 2) 
        
        for property in properties:
              
              if property['propertyUrl']:
                prop_id = property['propertyUrl']
                links = 'https://www.rightmove.co.uk' + prop_id
                
                yield res.follow(url=links, headers=self.headers,
                                 meta={'property': properties, 'id' : prop_id , 'postcode': postcode, 'filename': filename,
                                      'count': count}, callback=self.parse_listing)
                break
        
            
        try:
        
            #self.params['index'] = self.page_index
            try: 
                total_pages = properties['pagination']['total']
                print(total_pages)
                
                self.page_index +=24

               
            except:
                 total_pages = 1
                 print('PAGE %s | %s ' % (self.current_page, total_pages))  
                 
            if int(self.page_index/24) < total_pages:
                 next_page = res.url  + '&index=' + str(self.page_index)
                 print('\nnext_page:',next_page)                   
                 yield response.follow(url = next_page,
                                       header = self.headers,
                                       callback = self.parse_links)
               
               
            elif int(self.page_index/24) >= total_pages:
                  self.current_page = 1  
                  print('last-page:',self.current_page)
                      

        except:
          pass
          print('only single page',self.current_page) 


    def parse_links(self, res):
        print('\nok\n')


# main driver
if __name__ == '__main__':
    # run scrapers
    process = CrawlerProcess()
    process.crawl(soldhouses)
    process.start()
    
    #soldhouses.parse_links(soldhouses,'')

