import numpy as np

from helper import get_json, write_json

'''2D matrix whose rows are ingredients and cols are recipes.
A 1 denotes the occurence of an ingredient in a given recipe.'''
RECIPE_MATRIX = np.array(get_json('recipe_matrix.json'))

ALL_INGREDS = get_json('all_ingreds_filtered.json')
INGRED_TO_IX = {k: i for i, k in enumerate(ALL_INGREDS)}
IX_TO_INGRED = {i: k for i, k in enumerate(ALL_INGREDS)}

RECIPE_DATA = get_json('recipe_data_filtered.json')
IX_TO_RECIPE = {i: (r['title'], r['url']) for i, r in enumerate(RECIPE_DATA)}


def get_ranked_ingreds(ranked_ixs, match_ingred_sum):
    """Return dict of ingred and how often they coocurr."""
    ranked_ingreds = {}
    for ranked_ix in ranked_ixs:
        cooccurrences = match_ingred_sum[ranked_ix]
        if cooccurrences == 0:
            break
        ranked_ingreds[IX_TO_INGRED[ranked_ix]] = cooccurrences
    return ranked_ingreds


def get_match_recipes(match_recipe_ixs):
    return [IX_TO_RECIPE[ix] for ix in match_recipe_ixs]


def search(input_ingreds):
    """Return co-ocurring ranked ingreds and the recipes they occur in."""

    if isinstance(input_ingreds, str):
        input_ingreds = [input_ingreds]
    input_ixs = [INGRED_TO_IX[ingred] for ingred in input_ingreds]

    # Get only rows for our ingreds
    ingred_rows = RECIPE_MATRIX[input_ixs]
    # for each recipe, sum occurences of all our ingred.
    ingred_sum = np.sum(ingred_rows, 0)
    # Check where this sum equals the len of our ingred list.
    # This ensures we only get recipes that contain all our ingreds.
    match_recipe_ixs = np.argwhere(ingred_sum == len(input_ixs))
    match_recipes_m = RECIPE_MATRIX[:, match_recipe_ixs.flatten()]

    # Then sum total occurences of each ingredient for each recipe.
    match_ingred_sum = np.sum(match_recipes_m, 1)

    # Get list of matched ingred indices in descending order
    ranked_ixs = np.flip(np.argsort(match_ingred_sum))

    # Remove indices of input_ingreds from our ranked_ixs
    ix_to_remove = set(input_ixs)
    ranked_ixs = (ix for ix in ranked_ixs if ix not in ix_to_remove)

    ranked_ingreds = get_ranked_ingreds(ranked_ixs, match_ingred_sum)
    match_recipes = get_match_recipes(match_recipe_ixs.flatten())

    return ranked_ingreds, match_recipes


def get_ranked_ingreds_from_cooc(ingred):
    ingreds = get_json('all_ingreds_filtered.json')
    ingred_to_ix = {k: v for v, k in enumerate(ingreds)}
    ix_to_ingred = {v: k for v, k in enumerate(ingreds)}

    cooc = np.array(get_json('cooc.json'))

    ingred_ix = ingred_to_ix[ingred]
    ranked_ixs = np.argsort(cooc[ingred_ix])
    ranked_ixs = np.flip(ranked_ixs)

    ranked_ingreds = {}
    for ranked_ix in ranked_ixs:
        cooccurrences = cooc[ingred_ix, ranked_ix]
        if cooccurrences == 0:
            break
        ranked_ingreds[ix_to_ingred[ranked_ix]] = cooccurrences

    return ranked_ingreds


def main():
    pass

if __name__ == "__main__":
    main()

