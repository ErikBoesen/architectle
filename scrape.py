import requests
from bs4 import BeautifulSoup
import json

WEBSITE_ROOT = 'http://wirednewyork.com'

print('Getting Wired New York list')
html = requests.get(WEBSITE_ROOT + '/skyscrapers/alphabetical/').text
soup = BeautifulSoup(html)
lis = soup.find('div', {'id': 'primary'}).find_all('li')
print(len(lis))
print(lis[0])

buildings = []
for li in lis:
    a = li.find('a')
    if a is None or not a.attr['href'].startswith(WEBSITE_ROOT):
        continue
    name, year = li.text.split(' (')
    year = int(year.strip(')'))
    building = {
        'name': name,
        'year': year,
    }
    html = requests.get(a.attr['href'])
    soup = BeautifulSoup(html)
    if soup.find('img')['src'] == (WEBSITE_ROOT + '/images/nav/wny_new_logo.jpg'):
        images = soup.find_all('img')[1:]
    else:
        content = soup.find('div', {'id': 'content'})
        images = content.find_all('images')
    if len(images) == 0:
        continue
    building['images'] = [image['src'] for image in images]
    buildings.append(building)

