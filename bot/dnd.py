import re
import difflib
import requests
from bs4 import BeautifulSoup

urls = {
    'list': 'https://www.aidedd.org/dnd-filters/',
    'item': 'https://www.aidedd.org/dnd/'
}

endpoints = {
    'sort': 'sorts.php',
    'don': 'dons.php',
    'invoc': 'invocations-occultes.php',
    'monstre': 'monstres.php',
    'objet': 'objets-magiques.php',
    'poisons': 'poisons.php',
    'herbes': 'herbes.php'
}


def get_soup(key, value=None):
    if value:
        value = re.sub(r'\W', '-', value).lower()
        request = requests.get(f'{urls["item"]}{endpoints[key]}?vf={value}')
    else:
        request = requests.get(f'{urls["list"]}{endpoints[key]}')
    return BeautifulSoup(request.text, 'html.parser')


def is_in_or_close(soup, item):
    items = []
    for tr in soup.find_all('tr'):
        try:
            items.append(tr.find_all('td')[1].find('a').get_text().lower())
        except (AttributeError, IndexError):
            pass
    if item in items:
        return item
    return difflib.get_close_matches(item, items, n=5)


def get_item_detail(key, value):
    item_names = is_in_or_close(get_soup(key), value)
    if type(item_names) == list and len(item_names) > 1:
        return f'"{value}" n\'existe pas.\nVouliez vous dire {", ".join(item_names)} ?'
    else:
        if type(item_names) == list:
            item_names = item_names[0]
            print(f'"{value}" n\'existe pas. Recherche de "{item_names}" à la place.')
        item_soup = get_soup(key, item_names)
        return item_soup.find(class_='bloc')
