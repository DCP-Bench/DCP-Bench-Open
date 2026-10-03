"""De Bruijn sequence B(base, n): a cyclic sequence of length base**n over 0..base-1 in which every length-n string occurs exactly once as a substring."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    base = instance["base"]  # size of the alphabet
    n = instance["n"]  # order: length of the substrings
    m = base ** n  # length of the sequence, and number of distinct substrings
    positions = range(m)
    symbols = range(base)
    words = range(m)  # a length-n string read as a base-`base` number

    model = gp.Model("de_bruijn_sequence")

    # sym[k, d] is 1 when position k of the sequence holds symbol d.
    sym = model.addVars(positions, symbols, vtype=GRB.BINARY, name="sym")
    for k in positions:
        model.addConstr(sym.sum(k, "*") == 1, name=f"position[{k}]")
    de_bruijn = [gp.quicksum(d * sym[k, d] for d in symbols) for k in positions]

    # word[i, w] is 1 when the substring starting at position i (wrapping
    # around the end) is the string w, whose digit j, most significant first,
    # is (w // base**(n-1-j)) % base.
    word = model.addVars(positions, words, vtype=GRB.BINARY, name="word")
    for i in positions:
        model.addConstr(word.sum(i, "*") == 1, name=f"one_word[{i}]")
        # Digit j of the substring at i is the symbol at position i + j: the
        # strings with digit d there account for exactly the symbol d. This
        # ties each substring to the sequence without a big positional sum.
        for j in range(n):
            k = (i + j) % m
            place = base ** (n - 1 - j)
            for d in symbols:
                model.addConstr(
                    gp.quicksum(word[i, w] for w in words if (w // place) % base == d) == sym[k, d],
                    name=f"digit[{i},{j},{d}]",
                )

    # All substrings are different.
    for w in words:
        model.addConstr(word.sum("*", w) <= 1, name=f"distinct[{w}]")

    return model, {"de_bruijn": de_bruijn}
