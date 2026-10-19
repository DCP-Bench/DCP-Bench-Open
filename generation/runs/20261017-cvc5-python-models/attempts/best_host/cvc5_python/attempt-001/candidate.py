# Best host: seat six guests around a round table so that no two neighbours
# are guests who do not get along. Output x lists the guests in seating order
# (0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank).
import cvc5.pythonic as cz

# Guests who will sit next to each other (from the description).
NEXT_TO = {
    0: [3, 5],  # Andrew: Dave, Frank
    1: [2, 4],  # Betty: Cara, Erica
    2: [1, 5],  # Cara: Betty, Frank
    3: [0, 4],  # Dave: Andrew, Erica
    4: [1, 3],  # Erica: Betty, Dave
    5: [0, 2],  # Frank: Andrew, Cara
}
ALLOWED = [(a, b) for a in NEXT_TO for b in NEXT_TO[a]]


def build(instance):
    n = 6
    x = [cz.Int(f"x_{i}") for i in range(n)]
    constraints = []

    # Arrange the guests in a seating order: each of the six seats holds one guest.
    constraints += [x[i] >= 0 for i in range(n)]
    constraints += [x[i] <= n - 1 for i in range(n)]
    constraints.append(cz.Distinct(x))

    # If two guests who do not get along are seated next to each other, it will create
    # conflict at dinner. Guests seated next to each other (round the table, seat 5 next
    # to seat 0) must be guests who will sit next to each other.
    for i in range(n):
        j = (i + 1) % n
        constraints.append(cz.Or([cz.And(x[i] == a, x[j] == b) for a, b in ALLOWED]))

    return constraints, {"x": x}
