import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

WEBSITE_ROOT = 'http://wirednewyork.com'


def clean_image_src(building_url, src):
    # Handle relative paths
    if src.startswith('/'):
        return WEBSITE_ROOT + src
    elif src.startswith('../'):
        # Handle '../' by navigating up the directory
        return urljoin(building_url, src)
    else:
        # Handle paths starting from the current directory
        return urljoin(building_url, src)

print('Getting Wired New York list')
html = requests.get(WEBSITE_ROOT + '/skyscrapers/alphabetical/').text
soup = BeautifulSoup(html, 'html.parser')
lis = soup.find('div', {'id': 'primary'}).find_all('li')
print(len(lis))
print(lis[0])

buildings = []
for li in lis:
    text = li.text.replace('\xa0', ' ')
    print('Parsing ' + text)
    a = li.find('a')
    if a is None or not '(' in text or not a['href'].startswith('/') or 'destroyed' in text or 'under construction' in text:
        print('Skipping unlinked building.')
        continue
    name = text[:-7]
    year = int(text[-5:-1])
    building = {
        'name': name,
        'year': year,
    }
    building_url = WEBSITE_ROOT + a['href']
    html = requests.get(building_url).text
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('img') is None:
        print('Found 404 page.')
        continue
    if soup.find('img')['src'].endswith('/images/nav/wny_new_logo.jpg'):
        images = soup.find_all('img')[1:]
    else:
        content = soup.find('div', {'id': 'content'})
        images = content.find_all('img')
    if len(images) == 0:
        continue
    building['images'] = [clean_image_src(building_url, image['src']) for image in images]
    buildings.append(building)

with open('website/public/buildings.json', 'w') as f:
    json.dump(buildings, f)