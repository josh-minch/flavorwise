import re
import csv

import numpy as np
import pandas as pd
import spacy

import helper

"""
nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])
lemmatizer = nlp.vocab.morphology.lemmatizer
"""


def filter_naive(ingreds, ingred_filters):
    """Return sublist of ingreds matching ingredients in filter."""
    filtered_ingreds = set()

    s_prog = create_filter_prog(ingred_filters['special'])
    g_prog = create_filter_prog(ingred_filters['general'])

    for ingred in ingreds:
        ingred = ingred.replace(',', '')
        ingred = ingred.replace('-', ' ')
        '''First check if ingred is found in list of special foods.
        These foods contain substrings found in more general food strings.
        For example, if ingred is 'sour cream', we must check for 'sour cream'
        before 'cream', otherwise the filter will incorrectly add 'cream' to
        filtered_ingreds.'''
        found_spec_ingred = check_ingred(ingred, s_prog)
        if found_spec_ingred:
            filtered_ingreds.add(found_spec_ingred)
        else:
            found_gen_ingred = check_ingred(ingred, g_prog)
            if found_gen_ingred:
                filtered_ingreds.add(found_gen_ingred)

    return list(filtered_ingreds)


def create_filter_prog(ingred_filter):
    """ Return regex prog that matches ingreds in filter.

    Prog is of the form (?:\bapples?\b|\bbeets?\b ... )
    which looks for any exact match of an ingredient (which we enforce
    through checking at word boundaries with \b), or that same match
    ending in an 's' or 'es'
    """
    pattern = [r'\b{}s?(es)?\b'.format(ingred) for ingred in ingred_filter]
    pattern = '|'.join(pattern)
    pattern = '(?:{})'.format(pattern)
    return re.compile(pattern)


def check_ingred(ingred_to_check, prog):
    """Return lemmatized ingred_to_check if it matches prog."""
    match = prog.search(ingred_to_check.lower())
    if match:
        ingred = match.group(0)
        return lemmatize(ingred)
    return None


def pluralize(ingred, all_ingreds):
    next_ingred_ix = all_ingreds.index(ingred) + 1
    next_ingred = all_ingreds[next_ingred_ix]

    suffixes = ['s', 'es', 'ies']

    for suffix in suffixes:
        if suffix == 'ies':
            plural = ingred[:-1] + suffix
        else:
            plural = ingred + suffix
        if plural == next_ingred:
            return plural


# TODO: Lemmatize with ML library instead of brute rule-based approach.
# To handle deficiencies (the inability to
# handle noun chunks like 'sweet potatoes):
# Break down multi word phrases into individual words and lemmatize
# each individually, or maybe only lemmatize the final word. Maybe
# check if a word ends in 's' before lemmatizing?
# Keep word substitutions like 'chile' and move to different function
# (consolidate_spelling?).
def lemmatize(ingred):
    split_ingred = ingred.split()

    for word in split_ingred:
        word_lemma = word
        # Handle chiles, chilis, chillies, chilly, etc
        if word[:4] == 'chil':
            word_lemma = 'chile'
        elif word == 'leaves':
            word_lemma = 'leaf'
        elif 'jalapeno' in word:
            word_lemma = 'jalapeño'

        split_ingred[split_ingred.index(word)] = word_lemma

    ingred = ' '.join(split_ingred)

    if ingred[-2:] == 'ss' or ingred[-2:] == 'us':
        pass
    elif ingred[-3:] == 'ies':
        ingred = ingred[:-3] + 'y'
    elif ingred[-3:] == 'oes':
        ingred = ingred[:-2]
    elif ingred[-4:] == 'shes' or ingred[-4:] == 'ches':
        ingred = ingred[:-2]
    elif ingred[-1:] == 's':
        ingred = ingred[:-1]

    return ingred
    """
    return lemmatizer(ingred, NOUN)[-1]

    tokens = nlp(ingred)
    chunk_lemma = [chunk.lemma_ for chunk in tokens.noun_chunks]
    if len(chunk_lemma) > 0:
        return chunk_lemma[0]
    else:
        return [token.lemma_ for token in tokens][0]

    w = Word(ingred)
    return w.lemmatize()
    """


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

    units = ['oz', 'ounce', 'lb', 'pound', 'g', 'grams',
             'kg', 'kilogram', 'teaspoon', 'tablespoon', 'cup']
    units = ['{}s?'.format(unit) for unit in units]
    reg_units = r'\b(?:' + '|'.join(units) + r')\b'

    prog = re.compile(reg_parentheses + '|' + reg_quantity + '|' + reg_units)

    ingred_stripped = []
    for ingred in ingredients:
        ingred_stripped.append(prog.sub('', ingred).strip())

    return ingred_stripped


def write_recipe_data_filtered(infile, outfile):
    """Filter recipes from infile and save to outfile as json."""
    data = helper.get_json(infile)
    ingred_filters = create_ingred_filters()

    # Remove duplicate recipes
    df = pd.DataFrame(data)
    df_unique = df[~df['title'].duplicated()]
    data = df_unique.to_dict('records')

    for recipe in data:
        filtered_ingreds = filter_naive(recipe['ingreds'], ingred_filters)
        recipe['ingreds'] = filtered_ingreds

    helper.write_json(data, outfile, 'w')


def write_all_ingreds(recipe_file_name, ingred_file_name):
    """Save json of all ingreds in recipe_file_name to ingred_file_name."""
    data = helper.get_json(recipe_file_name)

    ingreds = []
    for recipe in data:
        ingreds.append(recipe['ingreds'])
    ingreds = [ingred for sublist in ingreds for ingred in sublist]
    ingreds = list(set(ingreds))
    ingreds.sort()

    helper.write_json(ingreds, ingred_file_name, 'w')
    return ingreds


def write_all_ingreds_lemma(infile='all_ingreds_filtered.json',
                            outfile='all_ingreds_lemma.json'):
    """Save json of lemmatization of ingreds in infile to outfile."""
    ingreds = helper.get_json(infile)
    ingreds = [lemmatize(ingred) for ingred in ingreds]
    helper.write_json(ingreds, outfile, 'w')


def find_unrecognized_ingreds(ingreds):
    """Write ingredients not found by ingred_filters to csv"""
    open('unrecognized_ingreds.csv', 'w').close()

    ingred_filters = create_ingred_filters()

    for ingred in ingreds:
        found_spec_ingred = check_ingred(ingred, ingred_filters['special'])
        found_gen_ingred = check_ingred(ingred, ingred_filters['general'])

        if not (found_spec_ingred or found_gen_ingred):
            with open('unrecognized_ingreds.csv', 'a',
                      encoding='utf8', newline='') as outfile:
                recipe_writer = csv.writer(outfile)
                recipe_writer.writerow([ingred])


def write_recipe_matrix(outfile='recipe_matrix.json'):
    '''2D matrix whose rows are ingredients and cols are recipes.
    A 1 denotes the occurence of an ingredient in a given recipe.'''
    ingreds = helper.get_json('all_ingreds_filtered.json')
    recipes = helper.get_json('recipe_data_filtered.json')

    titles = []
    for recipe in recipes:
        titles.append(recipe['title'])

    df = pd.DataFrame(0, ingreds, titles)

    ingreds = set(ingreds)
    for recipe in recipes:
        recipe_ingreds = set(recipe['ingreds'])
        matches = recipe_ingreds & ingreds
        if len(matches) > 0:
            df.loc[list(matches), recipe['title']] = 1

    data = df.to_numpy()
    data = data.tolist()
    helper.write_json(data, outfile, 'w')


def get_cooc():
    df = pd.DataFrame(helper.get_json('recipe_matrix.json'))
    m = df.dot(df.transpose())
    np.fill_diagonal(m, 0)
    return m


def main():
    write_recipe_data_filtered('recipe_data.json', 'recipe_data_filtered.json')
    write_all_ingreds('recipe_data_filtered.json', 'all_ingreds_filtered.json')
    write_all_ingreds_lemma()
    write_recipe_matrix()


if __name__ == "__main__":
    main()
