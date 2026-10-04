# Map colouring: give each of six countries (Belgium, Denmark, France,
# Germany, Netherlands, Luxembourg) a colour 1, 2, ... so that neighbouring
# countries differ, using as few colours as possible (minimise the highest
# colour used).
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

# The problem statement fixes the six countries; the reference declares
# num_nodes = 6 rather than reading it from the data, so it is mirrored here.
NUM_NODES = 6


def build(instance):
    graph = instance["graph"]  # pairs of adjacent countries, numbered from 1

    pool = IDPool()
    # colors[i] is the colour of country i, 1..NUM_NODES as in the reference.
    # Coupled encoding: value literals for the output and the "different"
    # constraints, order literals for the highest colour below.
    colors = [Integer(f"colors_{i}", 1, NUM_NODES, encoding="coupled", vpool=pool)
              for i in range(NUM_NODES)]
    # highest is the largest colour used.
    highest = Integer("highest", 1, NUM_NODES, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=colors + [highest], vpool=pool)

    # Two neighbouring countries do not have the same colour.
    for i, j in graph:
        engine.add_not_equal(colors[i - 1], colors[j - 1])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # highest is at least every country's colour: a colour of v or more
    # forces highest to v or more.
    for c in colors:
        for v in range(2, NUM_NODES + 1):
            formula.append([-c.ge(v), highest.ge(v)])

    # Minimise the number of colours: each colour above 1 that highest
    # reaches pays 1.
    for v in range(2, NUM_NODES + 1):
        formula.append([-highest.ge(v)], weight=1)

    return formula, {"colors": colors}
