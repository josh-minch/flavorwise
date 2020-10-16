import json
import collections

import numpy as np
import pandas as pd

from helper import get_json, write_json

def get_ranked_ingreds(ingreds):
    """Return ingreds from recipes in order of occurence with input ingreds."""

    '''2D matrix whose rows are ingredientss and cols are recipes titles.
    A 1 denotes the occurence of an ingredient in a given recipe.'''
    recipe_matrix = np.array(get_json('recipe_matrix.json'))

    all_ingreds = get_json('all_ingreds_filtered.json')
    ingred_to_ix = {k: v for v, k in enumerate(all_ingreds)}
    ix_to_ingred = {v: k for v, k in enumerate(all_ingreds)}

    ixs = [ingred_to_ix[ingred] for ingred in ingreds]

    # Get only rows for our ingreds
    ingred_rows = recipe_matrix[ixs]
    # for each recipe, sum occurences of all ingreds.
    ingred_sum = np.sum(ingred_rows, 0)
    # check where this sum equals the len of our ingred list.
    # This ensures we only get recipes that contain all our ingreds.
    match_recipe_ixs = np.argwhere(ingred_sum == len(ixs))
    match_recipes_m = recipe_matrix[:, match_recipe_ixs.flatten()]

    # Then sum total occurences of each ingredient for each recipe.
    ingred_sum = np.sum(match_recipes_m, 1)

    ranked_ixs = np.flip(np.argsort(ingred_sum))
    ranked_ingreds = [ix_to_ingred[ix] for ix in ranked_ixs]

    ranked_ingreds = [
        ingred for ingred in ranked_ingreds if ingred not in ingreds]
    return ranked_ingreds


def make_recipe_matrix():
    ingreds = get_json('all_ingreds_filtered.json')
    recipes = get_json('recipe_data_filtered.json')

    titles = []
    for recipe in recipes:
        titles.append(recipe['title'])

    df = pd.DataFrame(0, ingreds, titles)

    ingreds = set(ingreds)
    for recipe in recipes:
        recipe_ingreds = set(recipe['ingreds'])
        matches = recipe_ingreds & ingreds
        if len(matches) > 0:
            df.loc[list(matches), recipe['title']] += 1

    return df.to_numpy()


def get_cooc(df):
    df = make_recipe_matrix()

    m = df.to_numpy()
    m = m.dot(m.transpose())
    np.fill_diagonal(m, 0)
    return m

def get_similar_ingreds(ingred):
    df = pd.read_json(get_json('cooc_pd.json'))
    df = df[ingred].sort_values(ascending=False)
    return df


def get_similar_ingreds_np(ingred):
    ingreds = get_json('all_ingreds_filtered.json')
    if ingred not in ingreds:
        return ['''my apologies, but we do not seem to have this'''
        '''particular ingredient in our databses at this time''']
    ingred_to_ix = {k: v for v, k in enumerate(ingreds)}
    ix_to_ingred = {v: k for v, k in enumerate(ingreds)}

    cooc = np.array(get_json('cooc.json'))

    ix = ingred_to_ix[ingred]
    ranked_ixs = np.argsort(cooc[ix])
    ranked_ixs = np.flip(ranked_ixs)

    ingreds = [ix_to_ingred[ix] for ix in ranked_ixs]

    return ingreds

def main():
    ingreds = ['bacon']
    print(get_ranked_ingreds(ingreds))


if __name__ == "__main__":
    main()
