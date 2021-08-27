import re

import pandas as pd

import helper

"""
nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])
lemmatizer = nlp.vocab.morphology.lemmatizer
"""


def filter_naive(ingreds, ingred_filters):
    """Return sublist of ingreds matching ingredients in filter."""
    filtered_ingreds = set()

    for ingred in ingreds:
        ingred = ingred.replace(',', '')
        ingred = ingred.replace('-', ' ')

        for ingred_filter in reversed(ingred_filters):
            prog = create_filter_prog(ingred_filter)
            found_ingred = check_ingred(ingred, prog)
            if found_ingred:
                filtered_ingreds.add(found_ingred)
                break

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
    """Checks if ingred_to_check matches prog and returns it lemmatized."""
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

    if 'garlic' in set(split_ingred) and 'clove' in set(split_ingred):
        ingred = 'garlic'
    elif 'garlic' in set(split_ingred) and 'cloves' in set(split_ingred):
        ingred = 'garlic'

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


def generate_ingred_filters(approved_ingreds):
    """Takes approved list of ingreds and returns list of ingred filter sets.

    Each filter contains more specific superstrings of the the previous. For
    example, the first filter may have 'rice', the second 'rice flour', the
    third 'brown rice flour', etc.
    """
    filters = []
    current_filter = approved_ingreds

    while current_filter:
        next_filter = set()
        for cur_ingred in current_filter:
            other_ingreds = set(current_filter)
            other_ingreds.remove(cur_ingred)
            for ingred_to_check in other_ingreds:
                if re.search(r'\b' + re.escape(cur_ingred) + r'\b',
                             ingred_to_check):
                    next_filter.add(ingred_to_check)

        filters.append(current_filter - next_filter)
        current_filter = next_filter

    return filters


def write_recipe_data_filtered(infile, outfile):
    """Filter recipes from infile and save to outfile as json."""
    data = helper.get_json(infile)
    with open('approved_ingreds', 'r', encoding="utf8") as f:
        approved_ingreds = set(f.read().splitlines())
    ingred_filters = generate_ingred_filters(approved_ingreds)

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


""" def find_unrecognized_ingreds(ingreds):
    Write ingredients not found by ingred_filters to csv
    open('unrecognized_ingreds.csv', 'w').close()

    ingred_filters = create_ingred_filters()

    for ingred in ingreds:
        found_spec_ingred = check_ingred(ingred, ingred_filters['special'])
        found_gen_ingred = check_ingred(ingred, ingred_filters['general'])

        if not (found_spec_ingred or found_gen_ingred):
            with open('unrecognized_ingreds.csv', 'a',
                      encoding='utf8', newline='') as outfile:
                recipe_writer = csv.writer(outfile)
                recipe_writer.writerow([ingred]) """


def write_recipe_matrix(outfile='recipe_matrix.json'):
    '''2D matrix whose rows are ingredients and cols are recipes.
    A 1 denotes the occurence of an ingredient in a given recipe.'''
    ingreds = helper.get_json('./static/all_ingreds_filtered.json')
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


def clean_approved_ingreds():
    with open('approved_ingreds', 'r', encoding="utf8") as f:
        ingreds = f.read().splitlines()
        # Remove duplicates
        ingreds = set(ingreds)
        ingreds.discard('')
        ingreds = list(ingreds)
        ingreds.sort()

    with open('approved_ingreds', 'w', encoding='utf8') as f:
        f.write('\n'.join(ingreds))


def main():
    clean_approved_ingreds()
    write_recipe_data_filtered('recipe_data.json', 'recipe_data_filtered.json')
    write_all_ingreds('recipe_data_filtered.json',
                      'static/all_ingreds_filtered.json')
    write_recipe_matrix()


if __name__ == "__main__":
    main()
