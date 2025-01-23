import requests
import datetime
import json
from bs4 import BeautifulSoup
import re

WIKI_ROOT = 'https://en.wikipedia.org'
INFOBOX_YEAR_PROPERTIES = (
    'Completed',
    'Built',
    'Construction finished',
    'Opened',
    'Construction started',
)
CITATION_RE = re.compile(r'\s*\[\d+\]|\s*\[[a-z]\]')
DASH_RE = re.compile(r'[\u2013\u2014-]')


def scrape_tallest_buildings_list(page_slug: str):
    html = requests.get(WIKI_ROOT + '/wiki/' + page_slug).text
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
        name = cells[COL_INDEX_NAME].text.strip()
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
        image_url = 'https:' + image_url

        buildings.append({
            'name': name,
            'image': image_url,
            'year': year,
        })

    return buildings


def scrape_individual_building_page(page_slug):
    html = requests.get(WIKI_ROOT + '/wiki/' + page_slug).text
    soup = BeautifulSoup(html, 'html.parser')

    infobox = soup.find('table', {'class': 'infobox'})
    if infobox is None:
        # would be cool to throw the page content to ChatGPT or something but that would be intense
        return None
    image = infobox.find('td', {'class': 'infobox-image'})
    if not image:
        return None
    image = image.find('img')
    image = 'https:' + image['src']

    name = soup.find('span', {'class': 'mw-page-title-main'}).text

    rows = infobox.find_all('tr')
    infobox_properties = {}
    for row in rows:
        th = row.find('th')
        td = row.find('td')
        if not (th and td):
            continue
        infobox_properties[th.text.strip()] = td.text.strip()

    for prop in INFOBOX_YEAR_PROPERTIES:
        if prop in infobox_properties:
            year = infobox_properties[prop]
            year = CITATION_RE.sub('', year)
            if prop == 'Built' and DASH_RE.search(year):
                year = year.split(DASH_RE.search(year).group(1))
            elif prop == 'Opened':
                # Find the first four-digit number in the year string
                year_match = re.search(r'\b(\d{4})\b', year)
                if year_match:
                    year = int(year_match.group(1))
                else:
                    continue  # If no year found, skip this property
            year = int(year)
            return {
                'name': name,
                'image': image,
                'year': year,
            }

    return None


def scrape_category(category_slug)



def deduplicate_buildings(buildings):
    seen_images = set()
    unique_buildings = []

    for building in buildings:
        if building['image'] not in seen_images:
            seen_images.add(building['image'])
            unique_buildings.append(building)

    return unique_buildings

buildings = []
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_New_York_City')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_Brooklyn')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_Queens')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_Staten_Island')

buildings = deduplicate_buildings(buildings)

with open('website/public/buildings.json', 'w') as f:
    json.dump(buildings, f)