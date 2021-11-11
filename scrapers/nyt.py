"""
Recipe ingredient scraper for https://cooking.nytimes.com/collections
"""

import requests
from bs4 import BeautifulSoup

from helper import get_json, write_json


def save_all_collections_recipe_urls():

    collection_hrefs = []
    collection_anchor_selector = """
        .results > .cards > .popular-collections-card >
        .popular-collections-card-container > a
        """
    next_page_selector = '#next-page>a'

    base_url = 'https://cooking.nytimes.com/collections'
    next_page_href = ''
    next_page_div = True

    while (next_page_div):
        r = requests.get(base_url + next_page_href)
        soup = BeautifulSoup(r.content, 'html.parser')

        collection_divs = soup.select(collection_anchor_selector)
        cur_page_hrefs = ['https://cooking.nytimes.com' +
                          c_a.get('href') for c_a in collection_divs]
        collection_hrefs += cur_page_hrefs

        next_page_div = soup.select(next_page_selector)
        if(next_page_div):
            next_page_href = next_page_div[0].get('href')

    write_json(collection_hrefs, 'urls/nyt_collections.json', 'w+')


def save_all_recipe_urls():
    collections = get_json('urls/nyt_collections.json')
    recipe_hrefs = []
    for collection in collections:
        r = requests.get(collection)
        soup = BeautifulSoup(r.content, 'html.parser')

        recipe_hrefs += ['https://cooking.nytimes.com' + anchor.get('href')
                         for anchor in soup.select('.image-anchor')]

    write_json(recipe_hrefs, 'urls/nyt_urls.json', 'w+')


def save_recipe_data():
    urls = get_json('urls/nyt_urls.json')
    recipe_data = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        ingreds = get_ingreds(soup)
        title = get_property(soup, 'og:title')
        image_url = get_property(soup, 'og:image')

        recipe = {'title': title, 'url': url,
                  'image_url': image_url, 'ingreds': ingreds,
                  'source': 'NYT Cooking'}
        recipe_data.append(recipe)

    write_json(recipe_data, 'data/nyt.json', 'w+')


def get_ingreds(soup):
    try:
        ingreds_ul = soup.find('ul', class_='recipe-ingredients')
        ingreds_spans = ingreds_ul.select('.ingredient-name')
        ingreds = [ingred_div.get_text(' ', strip=True)
                   for ingred_div in ingreds_spans]
    except AttributeError:
        ingreds = []
    return ingreds


def get_property(soup, property_name):
    property = soup.find('meta', property=property_name,
                         content=True).get('content')
    return property


def main():
    # save_all_collections_recipe_urls()
    # save_all_recipe_urls()
    # save_recipe_data()

    pass


if __name__ == "__main__":
    main()
