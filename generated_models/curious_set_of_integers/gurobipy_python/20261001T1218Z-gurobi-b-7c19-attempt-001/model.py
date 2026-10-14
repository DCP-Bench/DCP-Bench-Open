"""Curious set of integers (Gardner): extend {1, 3, 8, 120} so that the product of any two members is one less than a square."""
import math

import gurobipy as gp
from gurobipy import GRB

# The four given members belong to the problem statement, not the instance.
GIVEN = [1, 3, 8, 120]


def build(instance):
    n = instance["n"]
    max_val = instance["max_val"]
    if n <= len(GIVEN):
        raise ValueError("the set must have at least one member beyond the given four")
    new = range(n - len(GIVEN))

    model = gp.Model("curious_set_of_integers")
    # Square roots of products reach about 1100 here, so their squares carry
    # coefficients near 10^6; a tight tolerance keeps near-0 binaries exact.
    model.Params.IntFeasTol = 1e-9

    def is_square_root_of(k, value_bound):
        """The roots q with q^2 = k * x + 1 for some integer x in 0..value_bound,
        with q itself in the reference's root domain 0..max_val. Such q satisfy
        q^2 = 1 (mod k), which keeps the list short."""
        top = min(max_val, math.isqrt(k * value_bound + 1))
        return [q for q in range(1, top + 1) if (q * q - 1) % k == 0]

    # The given members already have the property among themselves.
    for a in range(len(GIVEN)):
        for b in range(a + 1, len(GIVEN)):
            root = math.isqrt(GIVEN[a] * GIVEN[b] + 1)
            if root * root != GIVEN[a] * GIVEN[b] + 1 or root > max_val or GIVEN[b] > max_val:
                model.addConstr(gp.LinExpr() >= 1, name=f"given_pair_fails[{a},{b}]")

    # For each new member x and each given member k, k * x + 1 is a square q^2,
    # so x = (q^2 - 1) / k. root[i, k][q] = 1 selects that q; the first given
    # member's selection also defines x itself.
    root = {}
    value = []
    for i in new:
        for k in GIVEN:
            qs = is_square_root_of(k, max_val)
            pick = model.addVars(qs, vtype=GRB.BINARY, name=f"root[{i},{k}]")
            model.addConstr(pick.sum() == 1, name=f"one_root[{i},{k}]")
            root[i, k] = (qs, pick)
        qs, pick = root[i, GIVEN[0]]
        value.append(gp.quicksum((q * q - 1) // GIVEN[0] * pick[q] for q in qs))
        # Every given member's root gives the same x.
        for k in GIVEN[1:]:
            qs_k, pick_k = root[i, k]
            model.addConstr(value[i] == gp.quicksum((q * q - 1) // k * pick_k[q] for q in qs_k),
                            name=f"square_with[{i},{k}]")

    # All members are different: a new member is none of the given ones ...
    qs0, _ = root[0, GIVEN[0]] if new else ([], None)
    for i in new:
        qs, pick = root[i, GIVEN[0]]
        for q in qs:
            if (q * q - 1) // GIVEN[0] in GIVEN:
                model.addConstr(pick[q] == 0, name=f"not_given[{i},{q}]")
    # ... and the new members differ from each other (x determines its root).
    if len(new) > 1:
        for q in qs0:
            model.addConstr(gp.quicksum(root[i, GIVEN[0]][1][q] for i in new) <= 1, name=f"distinct[{q}]")

    # Two new members x and y also need x * y + 1 to be a square p^2. x * y is
    # linear by disaggregating y over x's root selection; p is selected from
    # its admissible roots the same way.
    for i in new:
        for j in new:
            if j <= i:
                continue
            qs, pick = root[i, GIVEN[0]]
            part = model.addVars(qs, lb=0, ub=max_val, name=f"part[{i},{j}]")
            for q in qs:
                model.addConstr(part[q] <= max_val * pick[q])
            model.addConstr(part.sum() == value[j])
            product = gp.quicksum((q * q - 1) // GIVEN[0] * part[q] for q in qs)
            ps = [p for p in range(1, min(max_val, math.isqrt(max_val * max_val + 1)) + 1)]
            p_pick = model.addVars(ps, vtype=GRB.BINARY, name=f"pair_root[{i},{j}]")
            model.addConstr(p_pick.sum() == 1)
            model.addConstr(product + 1 == gp.quicksum(p * p * p_pick[p] for p in ps),
                            name=f"square_pair[{i},{j}]")

    # The number asked for is the last member of the set.
    return model, {"number": value[-1]}
