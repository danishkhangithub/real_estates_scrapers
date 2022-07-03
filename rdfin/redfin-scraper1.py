# packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import urllib
import os
import json
import datetime
import csv
import ast
import requests
from iteration_utilities import unique_everseen


# property scraper class
class ResidentialSale(scrapy.Spider):
    # scraper name
    name = 'therapists'

    base_url = 'https://www.redfin.com/city/11203/CA/Los-Angeles'

    # headers
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }

    cur_page_no = 1

    file =  'redfin.csv'
    try:
       if (os.path.exists(file) and os.path.isfile(file)):
           os.remove('redfin.csv')
           print('file deleted')
       else:
           print('file not found')
    except OSError:
       pass
    # custom settings
    custom_settings = {
        'CONCURRENT_REQUEST_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1
    }

    # general crawler
    def start_requests(self):

            # initial HTTP request
            yield scrapy.Request(
                url=self.base_url,
                headers=self.headers,

                callback=self.parse
            )

    def  parse(self,response):

         content = ''
         with open('redfin.html', 'r' ) as f:
             for line in f.read():
                 content += line
         response = Selector(text=content)

         properties = [script for script in response.css('script').getall() if '<script type="application/ld+json">' in script]
         for prop in properties:
           prop = prop.split('<script type="application/ld+json">')[-1]
           prop=prop.split('</script>')[0]


           prop = json.loads(prop)
           prop2 = json.dumps(prop, indent = 2)

           for data in prop:
               if isinstance(data, dict):
                   items =  {
                       'Name' : data['name'],
                       'Url' : data['url'],
                       'Address' : data.get('address', ''),


                   }

                   #print(items)

                   with open('redfin.csv','a', encoding = 'utf-8') as csv_file:
                       writer =  csv.DictWriter(csv_file, fieldnames = ['Name','Url','Address'])
                       #writer.writeheader()
                       writer.writerow(items)




         '''
         next_page_no = response.css('.goToPage:last-child::text').get()
         self.cur_page_no +=1
         try:
             if self.cur_page_no <= int(next_page_no):
                 next_page = self.base_url + '/page-' + str(self.cur_page_no)
                 #self.log('\n\n | \n\n ' %(int(self.cur_page_no, next_page_no)))
                 print('\n\n curr_page | next_page_no' % (self.cur_page_no, int(next_page_no)))
                 yield response.follow(
                         next_page,
                         headers = self.headers,
                         callback = self.parse,
                         dont_filter = True
                 )


                 print('\npage:', self.cur_page_no,'\n')
             else:
                print('\n Crawling complete\n')
         except Exception as e:
           print('\nerror\n', e)
         '''

# main driver
if __name__ == '__main__':
    # run scraper
#    process = CrawlerProcess()
#    process.crawl(ResidentialSale)
#    process.start()

     ResidentialSale.parse(ResidentialSale, '')
