"""
Recipe ingredient scraper for https://www.saveur.com/tags/recipes/
"""

import requests
from bs4 import BeautifulSoup

from helper import get_json, write_json


def save_all_recipe_urls():

    recipe_hrefs = []
    recipe_anchor_selector = """
        .Column-main > .Post > .Post-info > .Post-link
        """
    next_page_selector = '.Pagination-link--next'

    next_page_href = 'https://www.saveur.com/tags/recipes/'
    next_page_div = True

    while (next_page_div):
        r = requests.get(next_page_href)
        soup = BeautifulSoup(r.content, 'html.parser')

        recipe_anchors = soup.select(recipe_anchor_selector)
        cur_page_hrefs = [r_a.get('href') for r_a in recipe_anchors]
        recipe_hrefs += cur_page_hrefs

        next_page_div = soup.select(next_page_selector)
        if(next_page_div):
            next_page_href = next_page_div[0].get('href')

    write_json(recipe_hrefs, 'urls/saveur_urls.json', 'w+')


def save_recipe_data():
    urls = get_json('urls/saveur_urls.json')
    recipe_data = []
    for url in urls[8725:]:
        try:
            r = requests.get(url)
        except requests.exceptions.TooManyRedirects:
            continue
        if r.status_code == 404:
            continue
        soup = BeautifulSoup(r.content, 'html.parser')

        ingreds = get_ingreds(soup)
        title = get_property(soup, 'og:title')

        try:
            image_url_tag = soup.find(
                'meta', property='og:image', content=True)
        except AttributeError:
            pass

        if not image_url_tag:
            try:
                image_url_tag = soup.find(
                    'meta',  attrs={'name': 'twitter:image'}, content=True)
            except AttributeError:
                pass

        try:
            image_url = image_url_tag.get('content')
        except AttributeError:
            continue

        recipe = {'title': title, 'url': url,
                  'image_url': image_url, 'ingreds': ingreds,
                  'source': 'Saveur'}
        recipe_data.append(recipe)

    write_json(recipe_data, 'saveur_end.json', 'w+')


def get_ingreds(soup):
    try:
        ingreds_ul = soup.find('ul', class_='ingredients')
        ingreds_spans = ingreds_ul.select('.ingredient')
        ingreds = [ingred_div.get_text(' ', strip=True)
                   for ingred_div in ingreds_spans]
    except AttributeError:
        ingreds = []
    return ingreds


def get_property(soup, property_name):
    property_row = soup.find('meta', property=property_name, content=True)
    if property_row:
        property = property_row.get('content')
        return property
    else:
        raise AttributeError


def main():

    # save_all_recipe_urls()
    save_recipe_data()


if __name__ == "__main__":
    main()
