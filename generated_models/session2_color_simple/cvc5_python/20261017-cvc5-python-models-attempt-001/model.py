# Problem: session2_color_simple. Colour the countries (Belgium, Denmark, France,
# Germany, Netherlands, Luxembourg) with integers starting from 1 so that two
# neighbouring countries never share a colour. Minimise the number of colours used.
import cvc5.pythonic as cz


def build(instance):
    edges = instance["graph"]
    n = max(max(e) for e in edges)  # countries are numbered 1..n in the data
    c = [cz.Int(f"c{i}") for i in range(n)]
    m = cz.Int("m")  # number of colours used, equal to the largest colour

    # Each colour is an integer from 1 up to the number of countries.
    constraints = []
    for i in range(n):
        constraints.append(c[i] >= 1)
        constraints.append(c[i] <= n)

    # Two neighbouring countries cannot have the same colour.
    # The data lists the neighbouring pairs in 1-based numbering.
    for a, b in edges:
        constraints.append(c[a - 1] != c[b - 1])

    # The objective m is the largest colour used.
    # Every colour is at most m, and m is one of the colours.
    constraints.append(m >= 1)
    constraints.append(m <= n)
    for i in range(n):
        constraints.append(c[i] <= m)
    constraints.append(cz.Or([c[i] == m for i in range(n)]))

    return constraints, {"colors": c}, ("minimize", m)
