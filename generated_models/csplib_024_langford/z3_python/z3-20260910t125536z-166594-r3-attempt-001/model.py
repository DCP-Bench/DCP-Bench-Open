import z3


def build(instance):
    k = instance["k"]
    size = 2 * k
    sol = [z3.Int(f"sol_{j}") for j in range(size)]
    position = [z3.Int(f"position_{j}") for j in range(size)]
    constraints = [z3.And(value >= 1, value <= k) for value in sol]
    constraints += [z3.And(slot >= 0, slot <= size - 1) for slot in position]
    constraints.append(z3.Distinct(position))
    # sol is indexed by a decision variable, and z3 has no Element, so mirror
    # the declared sequence into an array and read it with Select.
    table = z3.Array("sol_table", z3.IntSort(), z3.IntSort())
    for j in range(size):
        constraints.append(z3.Select(table, j) == sol[j])
    for value in range(1, k + 1):
        first, second = position[value - 1], position[k + value - 1]
        # The two copies of `value` are value+1 apart, and both land on it.
        constraints.append(second == first + value + 1)
        constraints.append(z3.Select(table, first) == value)
        constraints.append(z3.Select(table, second) == value)
    return constraints, {"sol": sol}
