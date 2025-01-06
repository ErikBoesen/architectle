import requests
from bs4 import BeautifulSoup

WEBSITE_ROOT = 'http://wirednewyork.com/skyscrapers/alphabetical/'

print('Getting Wired New York list')
html = requests.get(WEBSITE_ROOT).text
soup = BeautifulSoup(html)
lis = soup.find('div', {'id': 'primary'}).find_all('li')
print(len(lis))
print(lis[0])