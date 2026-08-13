from paramita.solvers import SatSolver
from paramita.encoders import PbToCnfEncoder
from paramita import PbConstraint
import json

# Integers 0..100 as one-hot Booleans: men[i] is true iff there are i men (same for women, children).
DOMAIN = 101
solver = SatSolver.from_name("Cadical300")
encoder = PbToCnfEncoder.from_name("AdderEncoder")
next_var = 1


def alloc(n):
    global next_var
    lits = list(range(next_var, next_var + n))
    next_var += n
    for lit in lits:
        solver.add_lit(lit)
    return lits


def encode_eq(lits, weights, bound):
    encoder.encode(
        PbConstraint(lits=list(lits), weights=list(weights), op=PbConstraint.EQ, bound=int(bound)),
        container=solver,
    )


# Decision variables: number of men, women, and children
men = alloc(DOMAIN)
women = alloc(DOMAIN)
children = alloc(DOMAIN)
ones = [1] * DOMAIN
values = list(range(DOMAIN))
encode_eq(men, ones, 1)
encode_eq(women, ones, 1)
encode_eq(children, ones, 1)

# 100 people in total
encode_eq(men + women + children, values * 3, 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
encode_eq(
    men + women + children,
    [6 * i for i in values] + [4 * i for i in values] + values,
    200,
)
# Five times as many women as men  (men ≤ 20, otherwise 5×men > 100 people)
for i in range(21):
    solver.add_clause([-men[i], women[5 * i]])
for i in range(21, DOMAIN):
    solver.add_clause([-men[i]])

if not solver.solve():
    raise SystemExit("No solution found.")
assignment = set(solver.model())


def decode(lits):
    for value, lit in enumerate(lits):
        if lit in assignment:
            return value
    raise SystemExit("No value assigned.")


print(json.dumps({
    "men": decode(men),
    "women": decode(women),
    "children": decode(children),
}))
