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
current_year = datetime.date.today().year
IGNORED_PAGES = {
    'Butterfield_House_(New_York_City)'
}
IGNORED_CATEGORY_KEYWORDS = {
    'Demolished',
    'Former',
    'Railway',
    'Sculptures',
}
IGNORED_PAGE_KEYWORDS = {
}
IGNORED_IMAGE_KEYWORDS = {
    'locator',
    'map',

}

scraped_pages = set()
scraped_categories = set()

def get_original_image(image_page_url: str) -> str:
    print(image_page_url)
    html = requests.get(WIKI_ROOT + image_page_url).text
    soup = BeautifulSoup(html, 'html.parser')
    image_url = soup.find('div', {'class': 'fullImageLink'}).find('a')['href']
    image_url = 'https:' + image_url
    return image_url

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
        if year >= current_year:
            continue

        image_cell = cells[COL_INDEX_IMAGE]
        if image_cell is None:
            continue
        image_page_url = image_cell.find('a')
        if image_page_url is None:
            continue
        image_page_url = image_page_url['href']
        if 'UploadWizard' in image_page_url: # Ignore 'Upload image' links
            continue
        image_url = get_original_image(image_page_url)

        # Check if the image URL contains any ignored keywords
        if any(keyword in image_url for keyword in IGNORED_IMAGE_KEYWORDS):
            continue  # Skip this image if it contains ignored keywords

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
    if page_slug in IGNORED_PAGES:
        print('Skipping ignored page ' + page_slug)
        return None
    if any(keyword in page_slug for keyword in IGNORED_PAGE_KEYWORDS):
        print('Skipping page ' + page_slug + ' because it contains ignored keywords.')
        return None
    scraped_pages.add(page_slug)

    print('Scraping individual page: ' + page_slug)
    html = requests.get(WIKI_ROOT + '/wiki/' + page_slug).text
    soup = BeautifulSoup(html, 'html.parser')

    infobox = soup.find('table', {'class': 'infobox'})
    if infobox is None:
        # would be cool to throw the page content to ChatGPT or something but that would be intense
        return None

    image_links = infobox.select('.infobox-image a.mw-file-description')
    image_links = [link for link in image_links if not '.svg' in link['href']]

    # Filter out images with ignored keywords
    image_links = [link for link in image_links if not any(keyword in link['href'] for keyword in IGNORED_IMAGE_KEYWORDS)]

    if not image_links:
        return None
    # We will get the original image only if all requirements are satisfied at the end

    name = soup.find('h1', {'class': 'mw-first-heading'}).text

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
            year = year.replace('c.\u2009', '') # remove circa
            if DASH_RE.search(year):
                year = YEAR_RE.search(year).groups()[-1]
            else:
                year = YEAR_RE.search(year).groups()[0]
            year = int(year)
            if year > current_year:
                return None

            return {
                'name': name,
                'image': get_original_image(image_links[-1]['href']),
                'year': year,
            }

    return None


def scrape_category(category_slug, mandatory_category_keywords):
    if any(keyword in category_slug for keyword in IGNORED_CATEGORY_KEYWORDS):
        print('Skipping category ' + category_slug + ' because it contains banned keywords.')
        return []
    if mandatory_category_keywords is not None and not any(category_slug.endswith(keyword) for keyword in mandatory_category_keywords):
        print('Skipping category ' + category_slug + ' as it does not contain mandatory keywords.')
        return []  # Early exit if no mandatory keywords are found

    if category_slug in scraped_categories:
        print('Skipping already scraped category ' + category_slug)
        return []  # Early exit if already scraped
    scraped_categories.add(category_slug)

    print('Scraping category ' + category_slug)
    html = requests.get(WIKI_ROOT + '/wiki/Category:' + category_slug).text
    soup = BeautifulSoup(html, 'html.parser')

    buildings = []
    subcategory_links = soup.select('div.CategoryTreeItem a')
    for link in subcategory_links:
        if link.get('href') is None:
            print('Found hrefless link, skipping')
            continue
        subcategory_slug = link['href'].replace('/wiki/Category:', '')
        print('Recursing on subcategory ' + subcategory_slug)
        buildings += scrape_category(subcategory_slug, mandatory_category_keywords)

    page_links = soup.find('div', {'class': 'mw-category'}).find_all('a')
    for page_link in page_links:
        if page_link.get('href') is None:
            continue
        page_slug = page_link['href'].replace('/wiki/', '')
        building = scrape_individual_building_page(page_slug)
        if building is not None:
            buildings.append(building)

    return buildings

def deduplicate_buildings(buildings):
    seen_images = set()
    unique_buildings = []

    for building in buildings:
        if building and building['image'] not in seen_images:
            seen_images.add(building['image'])
            unique_buildings.append(building)

    return unique_buildings

def scrape_city(name: str, category_slugs=(), building_slugs=(), mandatory_category_keywords=None):
    buildings = []
    for category_slug in category_slugs:
        buildings += scrape_category(category_slug, mandatory_category_keywords)

    for building_slug in building_slugs:
        buildings += scrape_tallest_buildings_list(building_slug)

    buildings = deduplicate_buildings(buildings)

    with open(f'website/public/buildings_{name}.json', 'w') as f:
        json.dump(buildings, f)
# TODO: Have the person also choose what city it is and whether it's
scrape_city(
    'Chicago',
    category_slugs=(
        'Buildings_and_structures_in_Chicago',
    ),
    building_slugs=(

    ),
    mandatory_category_keywords=(
        'Chicago',
    ),
)
scrape_city(
    'NYC',
    category_slugs=(
        'Residential_buildings_in_New_York_City',
        'Commercial_buildings_in_New_York_City',
        'Historic_district_contributing_properties_in_New_York_City',
        'Government_buildings_in_New_York_City',
        'Libraries_in_New_York_City',
    ),
    building_slugs=(
        'List_of_tallest_buildings_in_New_York_City',
        'List_of_tallest_buildings_in_Brooklyn',
        'List_of_tallest_buildings_in_Queens',
        'List_of_tallest_buildings_in_Staten_Island',
    ),
    mandatory_category_keywords=(
        'New_York',
        'New_York_City',
        'Manhattan',
        'Brooklyn',
        'Bronx',
        'Queens',
        'Staten_Island',
    )
)
