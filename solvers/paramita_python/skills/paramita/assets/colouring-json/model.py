import json
import sys

from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf
from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

# Usage: python3 model.py [data.json]
# Reads a graph (node count and edge list) and minimises the number of colours.
# Extra keys in the file are ignored.
path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    data = json.load(f)
n = data["nodes"]
# Each clique is a list of nodes of any length (a ragged list); every pair of its nodes is an edge.
edges = {tuple(sorted((u, v))) for clique in data["cliques"] for u in clique for v in clique if u < v}
k = n  # at most one colour per node is ever needed

# x[v][c]: node v has colour c (one-hot); used[c]: some node has colour c.
x = [[Bool(f"x_{v}_{c}") for c in range(k)] for v in range(n)]
used = [Bool(f"used_{c}") for c in range(k)]
subject_to = [sum(x[v]) == 1 for v in range(n)]
subject_to += [~x[v][c] | used[c] for v in range(n) for c in range(k)]
subject_to += [~x[u][c] | ~x[v][c] for u, v in edges for c in range(k)]
subject_to = And(subject_to)

# Minimising the colours = maximising the negated count.
objective = -sum(used)

pool = DimacsVariablePool()
maxsat = MaxSatSolver.from_name("EvalMaxSAT2022")
constant = add_to_weighted_container(objective, subject_to, to_cnf, maxsat, pool)
if maxsat.solve() != MAXSAT_ANSWER.OPTIMAL:
    raise SystemExit("optimum not proven")
colours = -(constant + maxsat.benefit())
print(f"Colours: {colours}")
