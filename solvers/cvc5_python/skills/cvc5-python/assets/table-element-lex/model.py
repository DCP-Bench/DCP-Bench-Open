"""Table, element and lexicographic constraints: four workers, one shift
each (shift 0, 1 or 2), minimise the total cost.

Shows:
- table constraint by enumeration: Or over the allowed (shift, shift) pairs
  of consecutive workers
- element lookup by enumeration: cost[w][shift] through an If chain
- lexicographic order between two vectors, used to break the symmetry of
  workers 0 and 1, which have identical cost rows
- minimisation by tightening the total cost until unsat
"""
from cvc5.pythonic import *

W, S = 4, 3
cost = [[5, 2, 7], [5, 2, 7], [4, 6, 1], [3, 3, 3]]  # workers 0 and 1 are interchangeable
# consecutive workers may take only these shift pairs
allowed = [(0, 0), (0, 1), (1, 2), (2, 0), (2, 1), (1, 1), (2, 2)]


def element(row, index):
    """row[index] for a variable index in 0..len(row)-1, by enumeration."""
    expr = row[-1]
    for k in range(len(row) - 2, -1, -1):
        expr = If(index == k, row[k], expr)
    return expr


def lex_le(xs, ys):
    """xs <= ys in lexicographic order, for two equal-length lists."""
    if not xs:
        return BoolVal(True)
    return Or(xs[0] < ys[0], And(xs[0] == ys[0], lex_le(xs[1:], ys[1:])))


shift = [Int(f"shift_{w}") for w in range(W)]
s = SolverFor("QF_LIA")
s.add(*[And(v >= 0, v < S) for v in shift])
for w in range(W - 1):
    s.add(Or([And(shift[w] == a, shift[w + 1] == b) for a, b in allowed]))
s.add(lex_le([shift[0], shift[1]], [shift[1], shift[0]]))

total = Sum([element(cost[w], shift[w]) for w in range(W)])

best, best_shift = None, None
while True:
    result = s.check()
    if result != sat:
        break
    m = s.model()
    best = m.eval(total, model_completion=True).as_long()
    best_shift = [m.eval(v, model_completion=True).as_long() for v in shift]
    s.add(total < best)

if result == unknown:
    print(f"undecided: {s.reason_unknown()}; best so far {best}")
else:
    print(f"Optimal cost: {best}")
    print("shifts:", best_shift)
