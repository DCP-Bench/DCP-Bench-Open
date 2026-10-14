"""CMO 2012: find the smallest a >= min_a for which some b <= a has a - b prime and a * b a perfect square."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    min_a = instance["min_a"]
    max_val = instance["max_val"]  # upper bound of a, b and n (the reference's domains)
    bits = range(max_val.bit_length())

    model = gp.Model("cmo_2012")
    # The products below reach about max_val**2 and carry binaries as multipliers; a tolerance
    # on binaries of 1e-5 would leave a visible error, so integrality and feasibility are tight.
    model.Params.IntFeasTol = 1e-9
    model.Params.FeasibilityTol = 1e-9
    model.Params.NumericFocus = 3

    a = model.addVar(lb=min_a, ub=max_val, vtype=GRB.INTEGER, name="a")
    b = model.addVar(lb=1, ub=max_val, vtype=GRB.INTEGER, name="b")
    n = model.addVar(lb=0, ub=max_val, vtype=GRB.INTEGER, name="n")
    p = model.addVar(lb=2, ub=max_val, vtype=GRB.INTEGER, name="p")

    # p is a prime below max_val (the reference's list of primes): one-hot over the primes.
    primes = [q for q in range(2, max_val) if all(q % d for d in range(2, int(q ** 0.5) + 1))]
    is_p = model.addVars(primes, vtype=GRB.BINARY, name="is_p")
    model.addConstr(is_p.sum() == 1, name="one_prime")
    model.addConstr(p == gp.quicksum(q * is_p[q] for q in primes), name="p_is_prime")

    # a >= b and p = a - b.
    model.addConstr(a >= b, name="a_ge_b")
    model.addConstr(p == a - b, name="p_is_difference")

    # a * b = n * n. Two variables cannot be multiplied (it would cap the model at 200
    # variables, and the primes alone exceed that), so each product is written with one
    # factor in binary, x = sum of 2^k * bit[k], and x * y = sum of 2^k * (bit[k] * y), where
    # bit * y is a binary times a bounded integer, which is linear.
    def binary_product(x, y, tag):
        digits = model.addVars(bits, vtype=GRB.BINARY, name=f"{tag}_bit")
        model.addConstr(x == gp.quicksum(2 ** k * digits[k] for k in bits), name=f"{tag}_binary")
        parts = model.addVars(bits, lb=0, ub=max_val, vtype=GRB.INTEGER, name=f"{tag}_part")
        for k in bits:
            # parts[k] = digits[k] * y, with 0 <= y <= max_val
            model.addConstr(parts[k] <= max_val * digits[k], name=f"{tag}_part_up[{k}]")
            model.addConstr(parts[k] <= y, name=f"{tag}_part_le_y[{k}]")
            model.addConstr(parts[k] >= y - max_val * (1 - digits[k]), name=f"{tag}_part_ge[{k}]")
        return gp.quicksum(2 ** k * parts[k] for k in bits)

    model.addConstr(binary_product(b, a, "b_times_a") == binary_product(n, n, "n_times_n"), name="product_is_square")

    # b <= n <= a follows from a * b = n * n with b <= a; it narrows the search.
    model.addConstr(n <= a, name="n_le_a")
    model.addConstr(n >= b, name="n_ge_b")

    # Find the smallest a.
    model.setObjective(a, GRB.MINIMIZE)

    return model, {"a": a, "b": b, "n": n, "p": p}
