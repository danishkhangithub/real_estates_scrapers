#packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import urllib
import datetime
import re

#sold houses class
class soldhouses(scrapy.Spider):
      #scraper name
      name = 'rightmove2'
      #base url 
      base_url = 'https://www.rightmove.co.uk/house-prices/CR0.html?' 
      
      #page index
      page_index = 0
      
      #string query parameters
      params = {
         'country': 'england',
         'locationIdentifier': '',
         'searchLocation': '',
         'referrer' : 'landingPage'
           }
      
      #headers
      headers = {
             'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }

       #custom setting
       #custom_settings = {
             #uncomment to set accordingly
             #"CONCURRENT_REQUESTS_PER_DOMAIN":2,
             #"DOWNLOAD_TIMEOUT":1   #250 ms  of delay
        #    }     
         
      #on create 
      def __init__(self):

          #inti postcodes
          postcodes = ''
          
          # open "postcodes.json" 
          with open('postcodes.json', 'r') as json_file:
               for line in json_file.read():
                    postcodes += line
          #parse postcodes
          self.postcodes = json.loads(postcodes)

     
        

      #crawler's entry point
      def start_requests(self):
           #init filename
           filename = './output/Sold_houses_' + datetime.datetime.today().strftime('%Y-%m-%d-%H-%M') + '.jsonl'
           #postcodes count
           count = 0
           #init string query parameters
           for item in self.postcodes:
                self.page_index = 0
                self.params['locationIdendifier'] = item['locationId']
                self.params['searchLocation'] = item['postcode']
                url = self.base_url +urllib.parse.urlencode(self.params) 
                print(url)
                yield scrapy.Request(url = url, headers= self.headers, meta = {'postcode': item['postcode'], 'filename':filename, 'count':count}, callback = self.parse_links)
                count +=1
                break


      def parse_links(self,res):

#         response = Selector(res= text)
#          with open('res.html', 'w' ) as f:
#                   f.write(res.text)
      
#          postcode = res.meta.get('postcode')
#          filename = res.meta.get('filename')
#          count = res.meta.get('count')
#         #extract links
#         for card in res.css('div.propertyCard-content')
#         #debug selectors
          
          content = ''
          with open('res.html', 'r' ) as f:
              for line in f.read():
                 content += line
          res = Selector(text=content) 
          
         #extract basic features
          properties = ''.join([script for script in res.css("script::text").getall() if 'window.__PRELOADED_STATE__ = {"results":' in script]) 
          properties = json.loads(properties.split('window.__PRELOADED_STATE__ = ')[-1])
          properties = properties['results']['properties'] 
          print(properties['detailUrl'])
          '''
          for property in properties:
            if property['detailUrl']: 
               prop_id = property['detailUrl'].split('?prop=')[-1].split('&')[0]
               links = 'https://www.rightmove.co.uk/property-for-sale/property-'+ prop_id +'.html'
             
               yield res.follow(url = property['detailUrl'],headers = self.headers, meta = {'property':properties,'postcode': postcode, 'filename':filename, 'count':count}, callback = self.parse_listing)
               break
      def parse_listing(self,res):
         
          content = ''
          with open('res.html', 'r' ) as f:
              for line in f.read():
                 content += line
          res = Selector(text=content)    
          #extract features
          features = {
                  'id' : re.findall('\d+',res.url.split('/')[-1])
                   'url' = '',
                   'postcode' = '',
                   'title' = '',
                   'address' = '',
                   'price' = '',
                   'agent_link' = '',
                   'agent_name' = '',
                   'agent_address' = '',
                   'agent_phone' = '',
                   'image_urls' = '',
                   'floor_area' = '',,
                   'key_features' = '',
                   'full_descriptions' = ''
                     } 

          filename = res.meta.get('filename')
          with open(filename, 'a') as json_file:
                 json_file.write(json.dumps(features,indent = 2))
          '''
#main driver
if __name__ == '__main__':
#    #run scrapers
#    process = CrawlerProcess()
#    process.crawl(soldhouses)
#    process.start()   

     soldhouses.parse_links(soldhouses,'')
