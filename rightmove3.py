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

    # string query parameters
    params = {
        'locationIdentifier': '',
        'country': 'england',
        'searchLocation': '',
        'referrer': 'landingPage',
        #'index' : ''
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
            self.params['index'] = self.page_index
            url = self.base_url + urllib.parse.urlencode(self.params)
            
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
            total_pages = properties['pagination']['total']
            print(total_pages)
        
        #self.params['index'] = self.page_index
            try: 
                self.page_index +=24
                
                next_page = res.url  + '&index=' + str(self.page_index)
                print(next_page)
                

                     
            except Exception as e:
                 print(e)
                 pass 
        
        except:
          print('error', self.current_page)
        
        if int(self.page_index/24) <= int(total_pages):
                self.log('\n\n %s | %s\n\n ' %(self.page_index/24), total_pages)
                yield scrapy.Request(url=next_page, headers=self.headers,
                                 meta={'property': properties, 'id' : prop_id , 'postcode': postcode, 'filename': filename,
                                      'count': count}, callback=self.parse_links)     

    def parse_listing(self, res):            
                
        #content = ''
        #with open('res4.html', 'r' ) as f:
        #   for line in f.read():
        #       content += line
        #res = Selector(text=content)
                
        # extract features
        for card in res.css('div[class="_38rRoDgM898XoMhNRXSWGq"]'):
            features = {

                 'Id' : res.meta.get('id'),

                 'Url' : res.url,

                 'Postcode' : res.meta.get('postcode'),

                 'Title' : card.css('meta[itemprop="name"]::attr(content)')
                               .get(),
                 'Address' : card.css('h1[class="_2uQQ3SV0eMHL1P6t5ZDo2q"]::text').get(),
                 
                 'Price' :  card.css('div[class="_1gfnqJ3Vtd1z40MlC0MzXu"]')
                                .css('span *::text')
                                .get(),

                  'Agent_link' : card.css('div[class="RPNfwwZBarvBLs58-mdN8"]')
                                     .css('a::attr(href)')
                                     .get(),
 
                  'Agent_name' : card.css('div[class="RPNfwwZBarvBLs58-mdN8"]')
                                     .css('a::text ')
                                     .get(),

                  'Agent_address' : card.css('div[class="OojFk4MTxFDKIfqreGNt0"]::text')
                                        .get()
                                        .replace('\n','').replace('\r',''),

                  'Agent_phone' :  card.css('div[class="_3ycD_mvlqA4t74u_G8TZYf"]')
                                       .css('a[class="_3E1fAHUmQ27HFUFIBdrW0u"]::text')
                                       .get(),
                  
                  'Image_urls' :  card.css('div[class="_2TqQt-Hr9MN0c0wH7p7Z5p"]')
                                      .css('img::attr(src)')
                                      .getall(),

                  'Floor_area' :  card.css('div[class="hU5084-VL7PQNtssjH2DK"]')
                                      .css('a[class="hU5084-VL7PQNtssjH2DK"]')
                                      .css('img::attr(src)').getall(),

                  'Key_features' : card.css('ul[class="_1uI3IvdF5sIuBtRIvKrreQ"]')
                                        .css('li::text')
                                        .getall(),

                  'No_of_Bedroom' : card.css('div[class="_38rRoDgM898XoMhNRXSWGq"]')
                                        .css('div[class="_3mqo4prndvEDFoh4cDJw_n"]')
                                        .css('div[class="_1fcftXUEbWfJOJzIUeIHKt"]::text')
                                        .getall()[1].strip('x'),

                  'No_of_Bathroom' : '',

     
                  'Description' : ''.join([
                                        desc.strip('\r') for desc in card.css('div[class="OD0O7FWw1TjbTD4sdRi1_"]')
                                            .css('div::text')
                                            .getall() if desc != '']),

                  'Latitude' :   '',
                  'Longitude' :  ''
            

 





    
                   }

        #extract latitude and longitude
        properties2 = ''.join([script for script in res.css("script::text").getall() if 'window.PAGE_MODEL = {"propertyData":' in script])
        properties2 = json.loads((properties2.split('window.PAGE_MODEL = ')[-1]).replace(" ", ""))
        properties2 = properties2['propertyData']['streetView']
        properties3 = properties2['latitude']
        properties4 = properties2['longitude']
        
        try:
 
            features['Latitude'] = properties3
            features['Longitude'] = properties4
        except: 
            features['Latitude'] = ''
            features['Longitude'] = ''

        try:
           features['No_of_Bathroom'] =   res.css('div[class="_38rRoDgM898XoMhNRXSWGq"]').css('div[class="_3mqo4prndvEDFoh4cDJw_n"]').css('div[class="_1fcftXUEbWfJOJzIUeIHKt"]::text').getall()[2].strip('x')
        except:
           features['No_of_Bathroom'] = ''








        #print(json.dumps(features,indent = 2))
         
       



        filename = res.meta.get('filename')
        with open(filename, 'a') as json_file:
            json_file.write(json.dumps(features, indent=2))
       

# main driver
if __name__ == '__main__':
    # run scrapers
    process = CrawlerProcess()
    process.crawl(soldhouses)
    process.start()
    
    #soldhouses.parse_links(soldhouses,'')

