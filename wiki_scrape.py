import requests
import datetime
import json
from bs4 import BeautifulSoup

WIKI_ROOT = 'https://en.wikipedia.org'
html = requests.get(WIKI_ROOT + '/wiki/List_of_tallest_buildings_in_New_York_City').text
soup = BeautifulSoup(html, 'html.parser')

# Ignore first row, which is the header
rows = soup.find('table', {'class': 'wikitable'}).find('tbody').find_all('tr')[1:]
COL_INDEX_NAME = 1
COL_INDEX_IMAGE = 2
COL_INDEX_YEAR = 5

buildings = []
for row in rows:
    cells = row.find_all('td')
    if len(cells) != 9:
        # This is probably one tower in a set, like Silver Towers or 10 Columbus Circle.
        # Skip this as an earlier row will have had a picture of both with rowspan
        continue
    name = cells[COL_INDEX_NAME].text
    year = cells[COL_INDEX_YEAR].text.strip()
    if year == 'On hold':
        continue
    year = int(year)
    if year >= datetime.date.today().year:
        continue

    image_cell = cells[COL_INDEX_IMAGE]
    print(image_cell)
    if image_cell is None:
        continue
    image_page_url = image_cell.find('a')['href']
    html = requests.get(WIKI_ROOT + image_page_url).text
    soup = BeautifulSoup(html, 'html.parser')
    image_url = soup.find('div', {'class': 'fullImageLink'}).find('a')['href']

    buildings.append({
        'name': name,
        'images': [image_url],
        'year': year,
    })

with open('website/public/buildings.json', 'w') as f:
    json.dump(buildings, f)