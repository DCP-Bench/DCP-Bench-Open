"""Word design: find words over the letters A, C, G, T that differ pairwise and against reversed complements in at least 4 places, each with 4 letters from {C, G}."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]                  # length of each word
    num_words = instance["num_words"]  # number of words to find
    words_ = range(num_words)
    places = range(n)
    # Letters as the reference numbers them: A = 1, C = 2, G = 3, T = 4. The Watson-Crick
    # complement of letter l is 5 - l. These and the numbers 4 and 4 below are the problem's own.
    letters = range(1, 5)
    C, G = 2, 3
    strong, distance = 4, 4  # required letters from {C, G} per word; required number of differences

    model = gp.Model("word_design")

    # letter[i, j, a] is 1 when letter j of word i is a.
    letter = model.addVars(words_, places, letters, vtype=GRB.BINARY, name="letter")
    for i in words_:
        for j in places:
            model.addConstr(letter.sum(i, j, "*") == 1, name=f"one_letter[{i},{j}]")
    words = [[gp.quicksum(a * letter[i, j, a] for a in letters) for j in places] for i in words_]

    # Each word has 4 symbols from {C, G}.
    for i in words_:
        model.addConstr(gp.quicksum(letter[i, j, C] + letter[i, j, G] for j in places) == strong,
                        name=f"strong[{i}]")

    # Each pair of distinct words differs in at least 4 places. differs[i, k, j] may be 1 only
    # where the two words have different letters: for every letter a, the two cannot both be a.
    for i in words_:
        for k in range(i + 1, num_words):
            differs = model.addVars(places, vtype=GRB.BINARY, name=f"differs[{i},{k}]")
            for j in places:
                for a in letters:
                    model.addConstr(differs[j] + letter[i, j, a] + letter[k, j, a] <= 2,
                                    name=f"apart[{i},{k},{j},{a}]")
            model.addConstr(differs.sum() >= distance, name=f"distance[{i},{k}]")

    # For each pair of words x and y (x may be y), x reversed and the complement of y differ in
    # at least 4 places. The pair (y, x) gives the same places as (x, y), so each unordered pair
    # is posted once. Place j compares letter n-1-j of x with the complement of letter j of y.
    for i in words_:
        for k in range(i, num_words):
            differs = model.addVars(places, vtype=GRB.BINARY, name=f"rc_differs[{i},{k}]")
            for j in places:
                for a in letters:
                    model.addConstr(differs[j] + letter[i, n - 1 - j, a] + letter[k, j, 5 - a] <= 2,
                                    name=f"rc_apart[{i},{k},{j},{a}]")
            model.addConstr(differs.sum() >= distance, name=f"rc_distance[{i},{k}]")

    return model, {"words": words}
