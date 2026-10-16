# Colour the six countries (Belgium, Denmark, France, Germany, Netherlands, Luxembourg)
# so that neighbouring countries get different colours, using as few colours as possible.
from paramita.modelling import Bool, Or

# The problem statement lists six countries. Each one can take at most six colours.
N_COUNTRIES = 6
MAX_COLOURS = 6


def build(instance):
    # The instance lists neighbouring pairs as 1-based country numbers.
    edges = [(a - 1, b - 1) for a, b in instance["graph"]]

    # One-hot encoding: x[i][c] is true when country i gets colour c+1.
    x = [[Bool(f"x_{i}_{c}") for c in range(MAX_COLOURS)] for i in range(N_COUNTRIES)]

    cons = []

    # Each country gets exactly one colour.
    for i in range(N_COUNTRIES):
        cons.append(sum(x[i]) == 1)

    # Two neighbouring countries cannot have the same colour.
    for a, b in edges:
        for c in range(MAX_COLOURS):
            cons.append(~(x[a][c] & x[b][c]))

    # Output: the colour of each country, numbered from 1.
    colors = [sum((c + 1) * x[i][c] for c in range(MAX_COLOURS)) for i in range(N_COUNTRIES)]

    # Minimise the number of colours used: colour c is used when some country has it.
    colours_used = sum(Or([x[i][c] for i in range(N_COUNTRIES)]) for c in range(MAX_COLOURS))
    return cons, {"colors": colors}, ("minimize", colours_used)
