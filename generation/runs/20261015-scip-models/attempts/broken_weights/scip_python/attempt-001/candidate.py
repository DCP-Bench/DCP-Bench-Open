# Broken weight: a weight of m pounds broke into n pieces with whole-pound weights.
# The pieces must weigh every whole amount from 1 to m on a balance scale.
from pyscipopt import Model, quicksum


def build(instance):
    total = instance["m"]
    n = instance["n"]
    model = Model()

    # w[i] = weight of piece i, in whole pounds
    w = [model.addVar(name=f"w_{i}", vtype="I", lb=1, ub=total) for i in range(n)]

    # the pieces together make up the whole weight
    model.addCons(quicksum(w) == total)

    for t in range(1, total + 1):
        # to weigh t, each piece is on the object's pan (p = 1), on the other pan (q = 1),
        # or not used (p = q = 0); the signed weights must then balance to t
        p = [model.addVar(name=f"p_{t}_{i}", vtype="B") for i in range(n)]
        q = [model.addVar(name=f"q_{t}_{i}", vtype="B") for i in range(n)]
        # products p*w and q*w, linearised exactly since p and q are binary
        zp = [model.addVar(name=f"zp_{t}_{i}", vtype="I", lb=0, ub=total) for i in range(n)]
        zq = [model.addVar(name=f"zq_{t}_{i}", vtype="I", lb=0, ub=total) for i in range(n)]
        for i in range(n):
            # a piece is on at most one pan
            model.addCons(p[i] + q[i] <= 1)
            # zp = p * w[i]
            model.addCons(zp[i] <= total * p[i])
            model.addCons(zp[i] <= w[i])
            model.addCons(zp[i] >= w[i] - total * (1 - p[i]))
            # zq = q * w[i]
            model.addCons(zq[i] <= total * q[i])
            model.addCons(zq[i] <= w[i])
            model.addCons(zq[i] >= w[i] - total * (1 - q[i]))
        # the pieces on the object's pan (zq) and the other pan (zp) balance to t
        model.addCons(quicksum(zp) - quicksum(zq) == t)

    return model, {"weights": w}
