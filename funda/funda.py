# import packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import csv
import json
import os
from bs4 import BeautifulSoup
from multiprocessing import  Process

class Funda(scrapy.Spider):
    name = 'funda'

    base_url = 'https://www.fundainbusiness.nl/alle-bedrijfsaanbod/amsterdam/'

    # headers
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }

    house = 0

    results = []

    file = 'funda.csv'
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

    def start_requests(self):
      yield scrapy.Request(
             url = self.base_url,
             headers = self.headers,
             callback = self.parse_pagination
            )
    def parse_pagination(self, response):
        pages = response.css('.pagination-label+ a::attr(data-pagination-page)').get()

        for page in range(0,int(pages)):
            next_page = self.base_url + 'p' + str(page) + '/'
            page = page
            yield response.follow(
                url = next_page,
                headers = self.headers,
                meta = {'page_no' : int(page),
                       'total_pages': int(pages)},
                callback = self.parse_links
            )



    def parse_links(self, response):
        page_no = response.meta.get('page_no')
        total_pages = response.meta.get('total_pages')

        print('\npage_no: %s | Total_pages: %s\n' % (page_no, total_pages))

        for card in response.css('div[class= "search-result-main"]'):
            link = card.css('a::attr(href)').get()


            self.house +=1

            # go to all links in each page
            yield response.follow(
                url = link,
                headers = self.headers,
                meta = {'house': self.house,
                        'title' : card.css('h2[class = "search-result__header-title fd-m-none"] *::text').get().strip(),
                        'price' : card.css('span[class = "search-result-price"] *::text').get()
                       },
                callback = self.parse_listing
            )

    def parse_listing(self,response):
       house = response.meta.get('house')
       price = response.meta.get('price')
       title = response.meta.get('title')

       # load content to bs4
       soup = BeautifulSoup(response.body, 'html.parser')



       '''
       content = ''

       with open('funda1.html', 'r') as f:
           for line in f.read():
               content += line

       response = Selector(text = content)
       '''

       features = {
           'Name' : title,
           'Url' : response.url,
           'Price' : price,
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
         phone1 = response.css('.object-contact-show-phonenumber a::attr(href)').get().strip('tel:')
         features['Phone_No'] = phone1

       except Exception as e:
         pass

       if features['Phone_No'] == '':
           try:
              phone2 =  response.css('div[class = "contact-button__container is-expandible"] a::attr(href)').get().strip('tel:')
              features['Phone_No'] = phone2

           except Exception as e:
              pass

       try:

          phone3 = response.css('div[class = "object-contact-show-phonenumber"] a::attr(href)').get().strip('tel:')
          features['Phone_No'] = phone3
       except:
           pass

       try:
         phone4 = phone = soup.find('div',{'class': 'object-contact-show-phonenumber'}).find('a', href = True)
         phone4 = phone4['href'].strip('tel:')
         features['Phone_No'] = phone4
       except:
         pass

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


       #print(json.dumps(features, indent = 2))
       self.results.append(features)
       headers = features.keys()


       with open('funda.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter = ',',fieldnames = headers)
            writer.writeheader()
            writer.writerows(self.results)

       print('house no %s' %(house), 'Crawled')





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
