"""Minimum vertex cover: the fewest vertices that touch every edge."""
import clingo

EDGES = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (2, 5), (3, 6)]
VERTICES = range(1, 7)

PROGRAM = """
% Choose any set of vertices.
{ in(V) : vertex(V) }.

% Every edge needs at least one endpoint in the cover.
:- edge(A,B), not in(A), not in(B).

% Minimise the number of chosen vertices.
#minimize { 1,V : in(V) }.

#show in/1.
"""

ctl = clingo.Control()
ctl.configuration.solve.opt_mode = "optN"   # improving models; the last one is a proven optimum
ctl.add("base", [], PROGRAM)
ctl.add("base", [], "".join(f"vertex({v}).\n" for v in VERTICES)
        + "".join(f"edge({a},{b}).\n" for a, b in EDGES))
ctl.ground([("base", [])])

with ctl.solve(yield_=True) as handle:
    last = None
    for model in handle:
        if model.optimality_proven:
            last = model
    result = handle.get()

cover = sorted(a.arguments[0].number for a in last.symbols(shown=True))
print("Optimal:", result.exhausted and last.optimality_proven)
print("Minimum cover size:", last.cost[0])
print("Cover:", cover)
