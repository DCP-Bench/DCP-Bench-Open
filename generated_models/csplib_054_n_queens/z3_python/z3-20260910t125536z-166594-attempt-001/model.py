import z3


def build(instance):
    n = instance["n"]
    queens = [z3.Int(f"queens_{row}") for row in range(n)]
    constraints = [z3.And(queen >= 1, queen <= n) for queen in queens]
    # A queen per row already; distinct columns, and distinct diagonals in
    # both directions. z3 has no AllDifferent, so Distinct does the work.
    constraints.append(z3.Distinct(queens))
    constraints.append(z3.Distinct([queens[row] - row for row in range(n)]))
    constraints.append(z3.Distinct([queens[row] + row for row in range(n)]))
    return constraints, {"queens": queens}
