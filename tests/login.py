import json

import requests

cookies = {
    'arl': ':)',
    'comeback': '1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    "Content-Type": "type/plain;charset=UTF-8"
}

response = requests.post('https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&input=3&api_version=1.0&api_token=&cid=361312840', cookies=cookies, headers=headers)

print(response)
print(response.status_code)
print(response.url)
print(response.content)
with open('login_out.json', 'w') as f:
    json.dump(response.json(), f, indent=2)