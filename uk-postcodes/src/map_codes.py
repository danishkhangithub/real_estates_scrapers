import requests
import json
user_input = 'CRO'
code_url = 'https://www.rightmove.co.uk/typeAhead/uknostreet/'

count = 0

for char in user_input:
     if count == 2:
        code_url += '/'
        count = 0
    
     code_url += char
     count +=1
     print(code_url)  

res = requests.get(code_url).json()
print(json.dumps(res, indent = 2))
