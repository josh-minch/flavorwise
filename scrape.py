import json
import os
import re
import csv
import time

import pandas as pd
import spacy
import requests
from bs4 import BeautifulSoup, SoupStrainer

import helper


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


def filter_naive(ingreds, ingred_filters):
    """Return sublist of ingreds matching ingredients in filter."""
    filtered_ingreds = set()

    s_prog = create_filter_prog(ingred_filters['special'])
    g_prog = create_filter_prog(ingred_filters['general'])

    for ingred in ingreds:

        '''First check if ingred is found in list of special foods. These foods contain
        substrings found in more general food strings. For example, if ingred is
        'sour cream', we must check for 'sour cream' before 'cream', otherwise the filter
        will incorrectly add 'cream' to filtered_ingreds.'''

        found_spec_ingred = check_ingred(ingred, s_prog)
        if found_spec_ingred:
            filtered_ingreds.add(found_spec_ingred)
        else:
            found_gen_ingred = check_ingred(ingred, g_prog)
            if found_gen_ingred:
                filtered_ingreds.add(found_gen_ingred)

    return list(filtered_ingreds)


def create_filter_prog(ingred_filter):
    """ Return regex prog of the form (?:\bapples?\b|\bbeets?\b ... )
    which looks for any exact match of an ingredient (which we enforce
    through checking at word boundaries with \b), or that same match
    ending in an 's' """
    pattern = [r'\b{}s?(es)?\b'.format(ingred) for ingred in ingred_filter]
    pattern = '|'.join(pattern)
    pattern = '(?:{})'.format(pattern)
    return re.compile(pattern)


def check_ingred(ingred_to_check, prog):
    """Return ingredient from prog filter if one matches ingred_to_check."""
    match = prog.search(ingred_to_check.lower())
    if match:
        return match.group(0)
    return None


def create_ingred_filters():
    """Return dictionary of approved ingredient filters, stored as lists."""
    filter_files = ['general', 'special']

    ingred_filters = {}
    for filter_name in filter_files:
        with open(filter_name, encoding="utf8") as f:
            ingred_filter = f.read().splitlines()
            # Remove duplicates, empty lines
            ingred_filter = set(ingred_filter)
            ingred_filter.remove('')
            ingred_filter = list(ingred_filter)

            ingred_filters[filter_name] = ingred_filter

    return ingred_filters


def filter_nlp(ingreds):
    nlp = spacy.load('en_core_web_sm')
    ingreds_filtered = []

    for ingred in ingreds:
        doc = nlp(ingred)

        nouns = [chunk.text for chunk in doc.noun_chunks]

        ingreds_filtered += nouns

    return ingreds_filtered


def filter_regex(ingredients):
    # Regex for parenthetical statements like (100g)
    reg_parentheses = r'(\(.*?\))'
    # For numerals, decimals, fractions
    reg_quantity = r'([-]?[0-9]+[,.]?[0-9]*([\/][0-9]+[,.]?[0-9]*)*)'

    units = ['oz', 'ounce', 'lb', 'pound', 'g', 'grams', 'kg', 'kilogram', 'teaspoon', 'tablespoon', 'cup']
    units = ['{}s?'.format(unit) for unit in units]
    reg_units = r'\b(?:' + '|'.join(units) + r')\b'

    prog = re.compile(reg_parentheses +'|'+ reg_quantity +'|'+ reg_units)

    ingred_stripped = []
    for ingred in ingredients:
        ingred_stripped.append(prog.sub('', ingred).strip())

    return ingred_stripped


def write_recipe_data_filtered(recipe_file_name, filtered_file_name):
    """Save json of filtered recipes in recipe_file_name to filtered_file_name."""
    data = helper.get_json(recipe_file_name)
    ingred_filters = create_ingred_filters()

    # Remove duplicate recipes
    df = pd.DataFrame(data)
    df_unique = df[~df['title'].duplicated()]
    data = df_unique.to_dict('records')

    for recipe in data:
        filtered_ingreds = filter_naive(recipe['ingreds'], ingred_filters)
        recipe['ingreds'] = filtered_ingreds

    helper.write_json(data, filtered_file_name, 'w')


def write_all_ingreds(recipe_file_name, ingred_file_name):
    """Save json of all recipes in recipe_file_name to ingred_file_name."""
    data = helper.get_json(recipe_file_name)

    ingreds = []
    for recipe in data:
        ingreds.append(recipe['ingreds'])
    ingreds = [ingred for sublist in ingreds for ingred in sublist]
    ingreds = list(set(ingreds))
    ingreds.sort()

    helper.write_json(ingreds, ingred_file_name, 'w')
    return ingreds

def find_unrecognized_ingreds(ingreds):
    """Write ingredients not found by ingred_filters to csv"""
    open('unrecognized_ingreds.csv', 'w').close()

    ingred_filters = create_ingred_filters()

    for ingred in ingreds:
        found_spec_ingred = check_ingred(ingred, ingred_filters['special'])
        found_gen_ingred = check_ingred(ingred, ingred_filters['general'])

        if not (found_spec_ingred or found_gen_ingred):
            with open('unrecognized_ingreds.csv', 'a', encoding='utf8', newline='') as outfile:
                recipe_writer = csv.writer(outfile)
                recipe_writer.writerow([ingred])

def main():

    write_recipe_data_filtered('recipe_data.json', 'recipe_data_filtered.json')
    write_all_ingreds('recipe_data_filtered.json', 'all_ingreds_filtered.json')

if __name__ == "__main__":
    main()


