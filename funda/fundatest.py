# import packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import csv
import json
import os
from multiprocessing import  Process

class Funda(scrapy.Spider):
    name = 'funda'

    # headers
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }

    house = 0

    results = []

    file = 'fundatest.csv'
    try:
       if (os.path.exists(file)) and (os.path.isfile(file)):
          os.remove(file)
       else:
          print('file not found')
    except OSError:
       pass
    # custom settings
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI' : 'funda.csv',
        'CONCURRENT_REQUEST_PER_DOMAIN': 6,
        'CONCURRENT_REQUESTS_PER_IP' : 6,
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT' : 10,
        'AUTO_THROTTLE' : False,


    }

    url_links = []

    def start_requests(self):
      # read urls from csv
      with open('mix_data.csv', 'r') as csv_file:
          urls = csv.reader(csv_file)
          for url in urls:
              self.url_links.append(url)

      for url_link in self.url_links[1:]:
          link = url_link

          yield scrapy.Request(
                 url =  link[0],
                 headers = self.headers,
                 callback = self.parse_listing
                )

    def parse_listing(self,response):
       '''
       content = ''

       with open('funda1.html', 'r') as f:
           for line in f.read():
               content += line

       response = Selector(text = content)
       '''

       features = {
           'Name' : '',
           'Url' : response.url,
           'Description' : ''.join(list(filter(None,[res.replace('\n', '').strip() for res in  response.css('.object-description-body::text').getall()]))),
           'key_features' : [],
           'area_features' : [],
           'cordinates' : {
               'latitude' : '',
               'longitude' : '',

           },
           'Images' : '',


           'Phone_No' : ''


        }

       try:
          name = response.css('.object-header__title *::text').get()
          #features['Name'] = name
          if name == None:
             try:
               name = response.css('h1[class = "nieuwbouwproject-hero__name"]::text').get()
             except:
               features['Name'] = None
       except:
          #name = response.css('h1[class = "nieuwbouwproject-hero__name"]::text').get()
          features['Name'] = None
       features['Name'] = name


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

       try:
         image1 = response.css('div[class = "object-media-fotos-container relative overflow-hidden"]').css('div div img::attr(src)').getall()
         features['Images'] = ' '.join(image1)
       except Exception as e:
          print('Error:\t', e)

       if features['Images'] == '':
           try:
              image2 =  response.css('a img[class = "nieuwbouwproject-hero__image"]::attr(src)').get()
              features['Images'] = image2
           except:
             features['Images'] = None


#       try:
#         phone = response.css('.object-contact-show-phonenumber a::attr(href)').get().strip('tel:')
#         features['Phone_No'] = phone
#
#       except:
#         pass
#

       try:

          features['Phone_No'] =  response.css('div[class = "contact-button__container is-expandible"] a::attr(href)').get().strip('tel:')


       except:
            #phone2 =  response.css('div[class = "contact-button__container is-expandible"] a::attr(href)').get().strip('tel:')

            pass
            #features['Phone_No'] = None

#       try:
#          phone =  response.css('a[class = "fd-btn fd-btn--primary"]::attr(href)').get().strip('tel:')
#          features['Phone_No'] = phone
#
#       except:
#          features['Phone_No'] = None
#
#       try:
#         phone = response.css('div[class = "object-contact-show-phonenumber"] a::attr(href)').get().strip('tel:')
#         features['Phone_No'] = phone
#       except:
#         features['Phone_No'] = None
#
#


       #print(json.dumps(features, indent = 2))
       self.results.append(features)
       headers = features.keys()

       with open('fundatest.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter = ',',fieldnames = headers)
            writer.writeheader()
            writer.writerows(self.results)

       print(features)





# main driver
if __name__ == '__main__':
#  def crawl():
       process = CrawlerProcess()
       process.crawl(Funda)
       process.start()
       #Funda.parse_listing(Funda, '')

#  process = Process(target=crawl)
#  process.start()
#  print(process)
