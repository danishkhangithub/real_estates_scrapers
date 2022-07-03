# packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import urllib
import os
import json
import datetime

# property scraper class
class ResidentialSale(scrapy.Spider):
    # scraper name
    name = 'funda'

    base_url = 'https://www.fundainbusiness.nl/alle-bedrijfsaanbod/'

    # headers
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }
    file = './output/funda.json'
    try:
       if (os.path.exists(file)) and (os.path.isfile(file)):
          os.remove(file)
       else:
          print('file not found')
    except OSError:
       pass
    # custom settings
    custom_settings = {
        'CONCURRENT_REQUEST_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 2
    }

    area_radius = 5

    current_page = 0
    # general crawler
    def start_requests(self):

         # init filename
        filename = './output/Sold_houses_' + datetime.datetime.today().strftime('%Y-%m-%d-%H-%M') + '.jsonl'

        for postcode in range(1016,5000):
             self.current_page  = 0

             #postcodes country
             count = 0

             next_postcode = self.base_url + str(postcode)
             next_postcode = next_postcode + '/+' +  str(self.area_radius)  + 'km/p' + str(self.current_page) + '/'

             yield scrapy.Request(
                   url = next_postcode,
                   headers = self.headers,
                   meta = {
                      'postcode' : postcode,
                      'filename' : filename,
                      'count' : count
                    },
                   callback = self.parse_links
             )
             count += 1


    def parse_links(self, response):
         #extract meta data
         postcode = response.meta.get('postcode')
         filename = response.meta.get('filename')
         count = response.meta.get('count')

         for card in response.css('div[class= "search-result-main"]'):
              links = card.css('a::attr(href)').get()

              yield response.follow(
                    url = links,
                    headers = self.headers,
                    meta = {
                      'postcode' : postcode,
                      'filename' : filename,
                      'count' : count,
                      'title' : card.css('h2[class = "search-result__header-title fd-m-none"] *::text').get(),
                      'price' : card.css('span[class = "search-result-price"] *::text').get()
                      },
                     callback = self.parse_listing
                )
              break

         print('POSTCODE: %s | %s out of %s ' % (postcode,count, 8999))

         try:

           try:

             #extract total pages
             total_pages = response.css('div[class= "pagination-pages"]')
             total_pages =  total_pages.css('a *::text').getall()
             total_pages = max([int(page.strip())
                             for page in response.css('div[class= "pagination-pages"]')
                              .css('a *::text').getall()
                             if  page.strip().isdigit() ])

             #increment current_page counter
             self.current_page +=1

           except:
             total_pages = 1
             print('totl:',total_pages)
             print('PAGE %s | %s ' % (self.current_page, total_pages))

           if self.current_page < total_pages:
                next_page = self.base_url + str(postcode)
                next_page = next_page +  '/+' +  str(self.area_radius)  + 'km/pg' + str(self.current_page) + '/'
                print('NEXT_PAGE:', next_page)
                print('page %s | %s ' % (self.current_page, total_pages))

                yield response.follow(
                  url = next_page,
                  headers = self.headers,
                  meta = {
                     'postcode' : postcode,
                     'filename' : filename,
                     'count' : count
                   },
                  callback = self.parse_links
                  )
           elif self.current_page >= total_pages:
                  self.current_page = 1
                  print('last-page:',self.current_page)


         except:
           pass
           print('Only single page:',self.current_page)



    def parse_listing(self, response):

        postcode = response.meta.get('postcode')
        filename = response.meta.get('filename')
        title = response.meta.get('title')
        price = response.meta.get('price')

        '''
        content = ''
        with open('funda.html', 'r' ) as f:
             for line in f.read():
                 content += line
        response = Selector(text=content)
        '''
        features = {
           #'id',
           #'url',
           #'title' : title.strip(),
           #'postcode',
           'Address' :  ''.join([text.strip() for text in
                           response.css('h1[class= "fd-m-top-none fd-m-bottom-xs fd-m-bottom-s--bp-m"] *::text').getall()]),
           #'price' : price,
           'Description': ''.join(list(filter(None,[text.replace('\n', '').strip()
                           for text in response.css('div[class= "object-description-body"]::text').getall()]))),

           'key_features' : [],
           'area_features' : [],
           'cordinates' : {
               'latitude' : '',
               'longitude' : '',

           },
           'images' : [image.get().split(',')[0]
                      for image in
                      response.css('div[class = "object-media-foto "]')
                      .css('img::attr(srcset)')
                       ],



        }
        try:

            key_features = {}
            characteristics1 = response.css('h3[class = "object-kenmerken-list-header"] + dl[class = "object-kenmerken-list"]')
            characteristics1 = Selector(text = characteristics1.get()).css('dt::text').getall()

            characteristics2 = response.css('h3[class = "object-kenmerken-list-header"] + dl[class = "object-kenmerken-list"]')[0]

            characteristics_values = list(filter(None, [val.replace('\n','').strip() for val in characteristics2.css('dd *::text').getall()]))

            for index in range(0, len(characteristics_values)):
                key_features[characteristics1[index]] = characteristics_values[index]

            features['key_features'] = [key_features]
        except:
           pass



        area_features = {}
        area_charactartics = response.css('h3[class = "object-kenmerken-list-header"] + dl[class = "object-kenmerken-list"]')[1]
        area_characts = Selector(text = area_charactartics.get()).css('dt *::text').getall()
        #print(area_characts)
        #area_characts_value = area_charactartics.css('h3[class = "object-kenmerken-list-header"] + dl[class = "object-kenmerken-list"]')[0]

        area_characts_value = list(filter(None, [val.replace('\n','').strip() for val in area_charactartics.css('dd *::text').getall()]))
        #print(area_characts_value)
        for index in range(0, len(area_characts_value)):
            area_features[area_characts[index]] = area_characts_value[index]

        features['area_features'] = [area_features]

        try:
           location_data = ''.join([text.get()
                           for text in
                           response.css('script[type = "application/json"]::text')
                            if '"lat"' in text.get()][0])

           location_data = json.loads(location_data)

           features['cordinates'] = {
                'latitude' : location_data['lat'],
                'longitude' : location_data['lng']


           }
        except Exception as e:
           pass
           print('Errors', e)



        print(json.dumps(features, indent = 2))

        filename = response.meta.get('filename')
        with open(filename, 'a') as json_file:
            json_file.write(json.dumps(features, indent=2))


# main driver
if __name__ == '__main__':
    # run scraper
    process = CrawlerProcess()
    process.crawl(ResidentialSale)
    process.start()

    #ResidentialSale.parse_listing(ResidentialSale, '')
