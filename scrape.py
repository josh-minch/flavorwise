import json
import os

import requests
from bs4 import BeautifulSoup, SoupStrainer


def get_soup_local(path, strainer):
    with open(path, encoding="utf8") as f:
        return BeautifulSoup(f.read(), 'html.parser', parse_only=strainer)


def get_soup(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')


def crawl(next_url):
    if next_url:
        recipe_urls = request_recipe_urls(next_url)
        write_recipe_urls(recipe_urls)
        next_url = get_next_page_url(next_url)
        return crawl(next_url)


def get_next_page_url(current_page_url):
    soup = get_soup(current_page_url)
    next_page_row = soup.select_one(
        'div.ui-pagination-outer-wrap > a.ui-pagination-btn__next')
    if not next_page_row:
        return None
    if next_page_row:
        return next_page_row.get('href')


def request_recipe_urls(url):
    soup = get_soup(url)

    recipes_section = soup.select_one('#recipes')

    recipe_link_rows = recipes_section.select(
        'a.module__image-container.module__link')
    recipe_urls = []

    for link_row in recipe_link_rows:
        link = link_row.get('href')
        if not link:
            continue
        recipe_urls.append(link)

    return recipe_urls


def write_recipe_urls(recipe_urls):
    f = open('recipe_urls.txt', 'a')
    for url in recipe_urls:
        f.write(url + '\n')


def open_html(path):
    with open(path, 'rb') as f:
        return f.read()


def save_html(html, pathname):
    with open(pathname, 'wb') as f:
        f.write(html)


def extract_recipe_urls(filename):
    with open(filename) as f:
        urls = f.read().splitlines()
        return urls


def request_recipes_html(urls):
    path_base = 'html/serious'
    path_index = 0
    for url in urls:
        full_path = '{}{}.html'.format(path_base, str(path_index))

        if not os.path.exists(full_path):
            html = requests.get(url).content
            save_html(html, full_path)

        path_index += 1


def save_recipe_html_from_urls(filename):
    urls = extract_recipe_urls(filename)
    request_recipes_html(urls)


# TODO: Fix extract_recipe_data duplicate recipe entries
def extract_recipe_data(html_dir):
    data = []
    for html_path in os.scandir(html_dir):
        url = get_recipe_url(html_path)
        title = get_recipe_title(html_path)
        ingreds = get_unfiltered_ingreds(html_path)

        recipe = {'title': title, 'url': url, 'ingreds': ingreds}
        data.append(recipe)

    with open('recipe_data.json', 'w', encoding='utf8') as f:
        json.dump(data, f)


def get_recipe_url(html_path):
    strainer = SoupStrainer('meta', property='og:url')
    soup = get_soup_local(html_path, strainer)
    url_row = soup.find('meta', property='og:url', content=True)
    return url_row.get('content')


def get_recipe_title(html_path):
    strainer = SoupStrainer('meta', property='og:title')
    soup = get_soup_local(html_path, strainer)
    recipe_row = soup.find('meta', property='og:title', content=True)
    return recipe_row.get('content')


def get_unfiltered_ingreds(html_path):
    strainer = SoupStrainer('li', class_='ingredient')
    soup = get_soup_local(html_path, strainer)
    ingredient_rows = soup.select('.ingredient')
    return [ingredient_row.text for ingredient_row in ingredient_rows]


def main():
    pass


if __name__ == "__main__":
    main()
