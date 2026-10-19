# Problem: among
# Requires exactly m values in x to take one of the values in v. All other values
# may be anything larger than or equal to 0 and less than or equal to 7.
# Print the array x (x).

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]

    x = [cz.Int(f"x_{i}") for i in range(n)]

    constraints = []

    # All values may be anything larger than or equal to 0 and less than or equal to 7.
    # x is an array of length n (taken from the instance).
    for i in range(n):
        constraints.append(x[i] >= 0)
        constraints.append(x[i] <= 7)

    # Requires exactly m values in x to take one of the values in v.
    # A value is "in v" when it equals one of the entries of v.
    def in_v(xi):
        eqs = [xi == val for val in v]
        if len(eqs) == 1:
            return eqs[0]
        return cz.Or(eqs)

    if n > 0:
        if len(v) == 0:
            # Nothing is in an empty v: exactly m entries can only be met if m is 0.
            constraints.append(cz.BoolVal(m == 0))
        else:
            inside = [cz.If(in_v(x[i]), 1, 0) for i in range(n)]
            constraints.append(cz.Sum(inside) == m)
    else:
        constraints.append(cz.BoolVal(m == 0))

    return constraints, {"x": x}
