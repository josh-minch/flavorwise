import numpy as np

from sklearn.metrics.pairwise import cosine_similarity as cs

from helper import get_json, timer

'''2D matrix whose rows are ingredients and cols are recipes.
A 1 denotes the occurence of an ingredient in a given recipe.'''
RECIPE_MATRIX = np.array(get_json('recipe_matrix.json'))
INGRED_AXIS = 0
RECIPE_AXIS = 1

ALL_INGREDS = get_json('static/all_ingreds_filtered.json')
INGRED_TO_IX = {k: i for i, k in enumerate(ALL_INGREDS)}
IX_TO_INGRED = {i: k for i, k in enumerate(ALL_INGREDS)}

RECIPE_DATA = get_json('recipe_data_filtered.json')
IX_TO_RECIPE = {i: (r['title'], r['url']) for i, r in enumerate(RECIPE_DATA)}


def get_recommended(input_ingreds):
    if isinstance(input_ingreds, str):
        input_ingreds = [input_ingreds]

    match_recipe_ixs = get_match_recipe_ixs(input_ingreds)
    ranked_ingreds = get_ranked_ingreds(input_ingreds, match_recipe_ixs)
    match_recipes = get_match_recipes(match_recipe_ixs)

    return ranked_ingreds, match_recipes


def get_ranked_ingreds(input_ingreds, match_recipe_ixs):
    """Return ranked ingreds that occur most with input_ingreds."""
    if not input_ingreds:
        return

    input_ixs = [INGRED_TO_IX[ingred] for ingred in input_ingreds]
    match_recipes_m = RECIPE_MATRIX[:, match_recipe_ixs.flatten()]

    # Sum total occurences of each ingredient for each recipe.
    num_of_recipes = np.sum(match_recipes_m, 1)

    input_ix_rows = RECIPE_MATRIX[input_ixs]
    match_recipes_ix = np.argwhere(input_ix_rows == 1)[:, RECIPE_AXIS]
    match_recipes_vec = RECIPE_MATRIX[:, match_recipes_ix]
    cooc_ingred_ix = np.argwhere(match_recipes_vec == 1)[:, INGRED_AXIS]
    cooc_ingred_ix = np.unique(cooc_ingred_ix)

    cooc_ingred_vec = RECIPE_MATRIX[cooc_ingred_ix]
    ingred_vec = RECIPE_MATRIX[input_ixs]

    cosine_similarity = timer(cs)
    similarity_score = cosine_similarity(ingred_vec, cooc_ingred_vec)
    similarity_score = np.mean(similarity_score, axis=0)

    # Sort ingredients by similarity score in descending order
    ranked_ixs = cooc_ingred_ix[np.flip(np.argsort(similarity_score))]
    similarity_score = np.flip(np.sort(similarity_score))
    num_of_recipes = num_of_recipes[ranked_ixs]

    # Convert to native python types
    similarity_score = getattr(similarity_score, "tolist",
                               lambda: similarity_score)()
    num_of_recipes = getattr(num_of_recipes, "tolist",
                             lambda: num_of_recipes)()

    # Remove ingredients already in current ingreds
    #  and make score human-readable
    ix_to_remove = set(input_ixs)
    ranked_ingreds = [(IX_TO_INGRED[i], f'{round(100*s, 1)}%', n) for i, s, n in zip(
        ranked_ixs, similarity_score, num_of_recipes) if i not in ix_to_remove]

    return ranked_ingreds


def get_match_recipes(match_recipe_ixs):
    return [IX_TO_RECIPE[int(ix)] for ix in match_recipe_ixs]


def get_match_recipe_ixs(input_ingreds):
    if not input_ingreds:
        return []

    input_ixs = [INGRED_TO_IX[ingred] for ingred in input_ingreds]
    ingred_rows = RECIPE_MATRIX[input_ixs]

    # For each recipe, sum occurences of all our ingred.
    # Check where this sum equals the len of our ingred list.
    # This ensures we only get recipes that contain all our ingreds.
    ingred_sum = np.sum(ingred_rows, 0)
    match_recipe_ixs = np.argwhere(ingred_sum == len(input_ixs))
    return match_recipe_ixs


def main():
    pass


if __name__ == "__main__":
    main()
