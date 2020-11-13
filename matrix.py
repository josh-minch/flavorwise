import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from helper import Algorithm, get_json

'''2D matrix whose rows are ingredients and cols are recipes.
A 1 denotes the occurence of an ingredient in a given recipe.'''
RECIPE_MATRIX = np.array(get_json('recipe_matrix.json'))

ALL_INGREDS = get_json('all_ingreds_filtered.json')
INGRED_TO_IX = {k: i for i, k in enumerate(ALL_INGREDS)}
IX_TO_INGRED = {i: k for i, k in enumerate(ALL_INGREDS)}

RECIPE_DATA = get_json('recipe_data_filtered.json')
IX_TO_RECIPE = {i: (r['title'], r['url']) for i, r in enumerate(RECIPE_DATA)}


def get_recommended(input_ingreds, algo=Algorithm.BEST_MATCH):
    if isinstance(input_ingreds, str):
        input_ingreds = [input_ingreds]

    match_recipe_ixs = get_match_recipe_ixs(input_ingreds)

    # TODO: handle initial page load with no input_ingreds
    # with own function, rather than calling get_most_common here
    if not input_ingreds or algo == Algorithm.COMMON:
        ranked_ingreds = get_most_common(input_ingreds, match_recipe_ixs)
    elif algo == Algorithm.BEST_MATCH:
        ranked_ingreds = get_best_matches(input_ingreds)

    match_recipes = get_match_recipes(match_recipe_ixs)

    return ranked_ingreds, match_recipes


def get_match_recipes(match_recipe_ixs):
    return [IX_TO_RECIPE[int(ix)] for ix in match_recipe_ixs]


def get_match_recipe_ixs(input_ingreds):
    input_ixs = [INGRED_TO_IX[ingred] for ingred in input_ingreds]
    ingred_rows = RECIPE_MATRIX[input_ixs]

    # For each recipe, sum occurences of all our ingred.
    # Check where this sum equals the len of our ingred list.
    # This ensures we only get recipes that contain all our ingreds.
    ingred_sum = np.sum(ingred_rows, 0)
    match_recipe_ixs = np.argwhere(ingred_sum == len(input_ixs))
    return match_recipe_ixs


def get_most_common(input_ingreds, match_recipe_ixs):
    """Return ranked ingreds that occur most with input_ingreds."""
    input_ixs = [INGRED_TO_IX[ingred] for ingred in input_ingreds]
    match_recipes_m = RECIPE_MATRIX[:, match_recipe_ixs.flatten()]

    # Sum total occurences of each ingredient for each recipe.
    match_ingred_sum = np.sum(match_recipes_m, 1)

    # Get list of matched ingred indices in descending order
    ranked_ixs = np.flip(np.argsort(match_ingred_sum))

    # Remove indices of input_ingreds from our ranked_ixs
    ix_to_remove = set(input_ixs)
    ranked_ixs = (ix for ix in ranked_ixs if ix not in ix_to_remove)

    ranked_ingreds = get_ranked_ingreds(ranked_ixs, match_ingred_sum)

    return ranked_ingreds


def get_best_matches(input_ingreds):
    """Return ingredients ranked by cosine similarity to input_ingreds."""
    input_ixs = [INGRED_TO_IX[ingred] for ingred in input_ingreds]
    ingred_rows = RECIPE_MATRIX[input_ixs]

    # Get ingreds cosine similarity to average of input ingreds
    input_mean = np.mean(ingred_rows, 0).reshape(1, -1)
    similarity_score = cosine_similarity(input_mean, RECIPE_MATRIX)[0]

    ranked_ixs = np.flip(np.argsort(similarity_score))
    similarity_score_sorted = np.flip(np.sort(similarity_score))

    ixs_to_remove = set(input_ixs)
    ranked_ingreds = {}
    for ix, score in zip(ranked_ixs, similarity_score_sorted):
        if score > 0 and ix not in ixs_to_remove:
            ranked_ingreds[IX_TO_INGRED[ix]] = score

    return ranked_ingreds


def get_ranked_ingreds(ranked_ixs, match_ingred_sum):
    """Return dict of ingred and how often they coocurr."""
    ranked_ingreds = {}
    for ranked_ix in ranked_ixs:
        cooccurrences = match_ingred_sum[ranked_ix]
        if cooccurrences == 0:
            break
        ranked_ingreds[IX_TO_INGRED[ranked_ix]] = cooccurrences
    return ranked_ingreds


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
