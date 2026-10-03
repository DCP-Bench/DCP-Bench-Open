"""KenKen: fill an n-by-n grid with 1..n, each once per row and column, so that every cage reaches its result by +, -, x or / (the operation is not given)."""
import gurobipy as gp
from gurobipy import GRB


def exponent(value, prime):
    """How many times prime divides value."""
    e = 0
    while value % prime == 0:
        value //= prime
        e += 1
    return e


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # each cage is [result, [[row, col], ...]] with 1-based cells
    cells = range(n)
    values = range(1, n + 1)
    primes = [p for p in range(2, n + 1) if all(p % q for q in range(2, p))]

    model = gp.Model("kenken")

    # is_[r, c, v] is 1 when cell (r, c) holds v; each cell holds one digit.
    is_ = model.addVars(cells, cells, values, vtype=GRB.BINARY, name="is")
    for r in cells:
        for c in cells:
            model.addConstr(is_.sum(r, c, "*") == 1, name=f"cell[{r},{c}]")
    x = [[gp.quicksum(v * is_[r, c, v] for v in values) for c in cells] for r in cells]

    # Each row and each column contains each digit exactly once.
    for v in values:
        for r in cells:
            model.addConstr(is_.sum(r, "*", v) == 1, name=f"row[{r},{v}]")
        for c in cells:
            model.addConstr(is_.sum("*", c, v) == 1, name=f"col[{c},{v}]")

    for k, (res, segment) in enumerate(cages):
        cage = [(r - 1, c - 1) for r, c in segment]

        if len(cage) == 2:
            # Two cells a, b: a + b, a * b, a / b, b / a, a - b or b - a equals
            # the result. pair[a, b] is the joint choice of the two digits,
            # created only for the digit pairs that satisfy one of the six;
            # its marginals are the two cells' digits, which makes the pair
            # exact without a product of variables.
            (r1, c1), (r2, c2) = cage
            allowed = [
                (a, b) for a in values for b in values
                if a + b == res or a * b == res or a * res == b or b * res == a or a - b == res or b - a == res
            ]
            pair = model.addVars(allowed, lb=0, ub=1, vtype=GRB.CONTINUOUS, name=f"pair[{k}]")
            for a in values:
                model.addConstr(gp.quicksum(pair[a, b] for (aa, b) in allowed if aa == a) == is_[r1, c1, a], name=f"first[{k},{a}]")
            for b in values:
                model.addConstr(gp.quicksum(pair[a, b] for (a, bb) in allowed if bb == b) == is_[r2, c2, b], name=f"second[{k},{b}]")
        else:
            # Any other cage: the digits sum to the result, or multiply to it.
            # use_sum is 1 for the sum and 0 for the product.
            use_sum = model.addVar(vtype=GRB.BINARY, name=f"use_sum[{k}]")
            model.addConstr((use_sum == 1) >> (gp.quicksum(x[r][c] for r, c in cage) == res), name=f"sum[{k}]")
            # A product of digits 1..n equals the result exactly when, for every
            # prime up to n, the digits' exponents of that prime add up to the
            # result's; this states the product linearly. A result with another
            # prime factor cannot be such a product.
            rest = res
            if res >= 1:
                for p in primes:
                    rest //= p ** exponent(res, p)
            if res < 1 or rest != 1:
                model.addConstr(use_sum == 1, name=f"no_product[{k}]")
            else:
                for p in primes:
                    digit_exponents = gp.quicksum(
                        exponent(v, p) * is_[r, c, v] for r, c in cage for v in values if exponent(v, p) > 0)
                    model.addConstr((use_sum == 0) >> (digit_exponents == exponent(res, p)), name=f"product[{k},{p}]")

    return model, {"x": x}
