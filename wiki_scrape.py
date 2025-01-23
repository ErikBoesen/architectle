import requests
import datetime
import json
from bs4 import BeautifulSoup
import re

WIKI_ROOT = 'https://en.wikipedia.org'
INFOBOX_YEAR_PROPERTIES = (
    'Completed',
    'Built',
    'Estimated completion',
    'Construction finished',
    'Opened',
    'Inaugurated',
    #'Construction started',
)
CITATION_RE = re.compile(r'\s*\[\d+\]|\s*\[[a-z]\]')
DASH_RE = re.compile(r'[\u2013\u2014-]')
YEAR_RE = re.compile(r'(\d{4})')

scraped_pages = set()
scraped_categories = set()

def scrape_tallest_buildings_list(page_slug: str):
    print('Scraping tallest buildings list: ' + page_slug)
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
        if image_cell is None:
            continue
        image_page_url = image_cell.find('a')['href']
        if 'UploadWizard' in image_page_url: # Ignore 'Upload image' links
            continue
        html = requests.get(WIKI_ROOT + image_page_url).text
        soup = BeautifulSoup(html, 'html.parser')
        image_url = soup.find('div', {'class': 'fullImageLink'}).find('a')['href']
        image_url = 'https:' + image_url

        buildings.append({
            'name': name,
            'image': image_url,
            'year': year,
        })
        print('Scraped ' + name)

    return buildings


def scrape_individual_building_page(page_slug):
    if page_slug in scraped_pages:
        print('Skipping already scraped page ' + page_slug)
        return None
    scraped_pages.add(page_slug)

    print('Scraping individual page: ' + page_slug)
    html = requests.get(WIKI_ROOT + '/wiki/' + page_slug).text
    soup = BeautifulSoup(html, 'html.parser')

    infobox = soup.find('table', {'class': 'infobox'})
    if infobox is None:
        # would be cool to throw the page content to ChatGPT or something but that would be intense
        return None

    images = infobox.find_all('img', {'class': 'mw-file-element'})
    # Skip maps if possible
    filtered_images = [img for img in images if not (img.find_parent('a', class_='mw-kartographer-map') or img.find_parent('div', class_='switcher-container'))]
    if filtered_images:
        image = 'https:' + filtered_images[-1]['src']  # Use the last valid image, earlier ones may be logos etc
    else:
        return None

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
            print(year)
            year = CITATION_RE.sub('', year)
            year = year.replace('c.\u2009', '') # remove circa
            if prop == 'Built':
                if DASH_RE.search(year):
                    year = DASH_RE.split(year)[-1]
                else:
                    year = YEAR_RE.search(year).groups()[0]
            elif prop in ('Opened', 'Inaugurated', 'Construction finished', 'Completed'):
                # Find the first four-digit number in the year string
                year_match = YEAR_RE.search(year)
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


def scrape_category(category_slug):
    if category_slug in scraped_categories:
        print('Skipping already scraped category ' + category_slug)
        return []  # Early exit if already scraped
    scraped_categories.add(category_slug)

    print('Scraping category ' + category_slug)
    html = requests.get(WIKI_ROOT + '/wiki/Category:' + category_slug).text
    soup = BeautifulSoup(html, 'html.parser')

    buildings = []
    subcategory_links = soup.select('div.CategoryTreeItem a')
    print(f'Found {len(subcategory_links)} subcategory links! I\'m sure none of these will cause complications!')
    for link in subcategory_links:
        if link.get('href') is None:
            print('Found hrefless link, skipping')
            continue
        subcategory_slug = link['href'].replace('/wiki/Category:', '')
        print('Recursing on subcategory ' + subcategory_slug)
        buildings += scrape_category(subcategory_slug)

    page_links = soup.find('div', {'class': 'mw-category'}).find_all('a')
    for page_link in page_links:
        page_slug = page_link['href'].replace('/wiki/', '')
        building = scrape_individual_building_page(page_slug)
        if building is not None:
            buildings.append(building)

    return buildings

def deduplicate_buildings(buildings):
    seen_images = set()
    unique_buildings = []

    for building in buildings:
        if building['image'] not in seen_images:
            seen_images.add(building['image'])
            unique_buildings.append(building)

    return unique_buildings

buildings = []
buildings += scrape_category('Residential_buildings_in_New_York_City')
buildings += scrape_category('Historic_district_contributing_properties_in_New_York_City')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_New_York_City')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_Brooklyn')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_Queens')
buildings += scrape_tallest_buildings_list('List_of_tallest_buildings_in_Staten_Island')

buildings = deduplicate_buildings(buildings)

with open('website/public/buildings.json', 'w') as f:
    json.dump(buildings, f)