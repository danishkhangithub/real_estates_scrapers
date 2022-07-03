import requests
from bs4 import BeautifulSoup
import json
import re

url = 'https://en.wikipedia.org/wiki/List_of_postcode_districts_in_the_United_Kingdom'

response = requests.get(url)

content = BeautifulSoup(response.text, 'lxml')

table = content.find('table', {'class': 'wikitable sortable'})

rows = table.find_all('tr')


cols = [[col.text.strip('\n') 
       for col in 
       row.find_all('td')]
       for row in 
       rows]


#init raw data 
raw_data = []
#init postcodes
postcodes = []



for col in cols[1:]:
    raw_data.append(col[1])

ranges = re.findall(r'\w+\d+','\n'.join(raw_data))

print(ranges)
