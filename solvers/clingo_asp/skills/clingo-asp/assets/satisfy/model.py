"""Colour a small graph with three colours so that no edge joins two equal colours."""
import sys

import clingo

NODES = range(1, 7)
EDGES = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6)]

PROGRAM = """
colour(red;green;blue).

% Every node gets exactly one colour.
1 { assign(N,C) : colour(C) } 1 :- node(N).

% Adjacent nodes must not share a colour.
:- edge(A,B), assign(A,C), assign(B,C).

#show assign/2.
"""

ctl = clingo.Control()
ctl.add("base", [], PROGRAM)
ctl.add("base", [], "".join(f"node({n}).\n" for n in NODES)
        + "".join(f"edge({a},{b}).\n" for a, b in EDGES))
ctl.ground([("base", [])])

with ctl.solve(yield_=True) as handle:
    models = [m.symbols(shown=True) for m in handle]
    result = handle.get()

print("Satisfiable:", result.satisfiable)
if not result.satisfiable:
    sys.exit(1)

colour = {atom.arguments[0].number: str(atom.arguments[1]) for atom in models[0]}
for n in NODES:
    print(f"node {n}: {colour[n]}")
print("Valid colouring:", all(colour[a] != colour[b] for a, b in EDGES))
