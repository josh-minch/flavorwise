import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from helper import get_json

if __name__ == "__main__":
    cooc = get_json('cooc.json')
    ingreds = get_json('all_ingreds_filtered.json')
    G = nx.from_numpy_array(np.array(cooc))
    nx.draw(G)
    plt.show()