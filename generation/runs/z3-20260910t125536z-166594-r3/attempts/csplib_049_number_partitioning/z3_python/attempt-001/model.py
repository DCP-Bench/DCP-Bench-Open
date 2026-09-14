import z3


def build(instance):
    n = instance["n"]
    half = n // 2
    first = [z3.Int(f"a_{i}") for i in range(half)]
    second = [z3.Int(f"b_{i}") for i in range(half)]
    constraints = [z3.And(value >= 1, value <= n) for value in first + second]
    constraints.append(z3.Distinct(first + second))
    constraints.append(z3.Sum(first) == z3.Sum(second))
    # Equal sums of squares as well; written as value * value rather than **.
    constraints.append(z3.Sum([value * value for value in first])
                       == z3.Sum([value * value for value in second]))
    return constraints, {"A": first, "B": second}
