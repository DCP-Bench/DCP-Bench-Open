"""Low autocorrelation binary sequences: choose a sequence of n values +1/-1 that minimises the energy, the sum over all shifts of the squared periodic autocorrelation."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]  # length of the sequence
    places = range(n)

    model = gp.Model("autocorrelation")

    # up[i] is 1 when sequence[i] = +1 and 0 when it is -1 (the reference excludes 0).
    up = model.addVars(places, vtype=GRB.BINARY, name="up")
    sequence = [2 * up[i] - 1 for i in places]

    # differ[i, j] is 1 when sequence[i] and sequence[j] have opposite signs, so that the
    # product sequence[i] * sequence[j] equals 1 - 2 * differ[i, j]. The four rows make it the
    # exclusive or of up[i] and up[j]. This replaces the product of two variables, which
    # would put the model under the 200-variable limit for quadratic terms.
    differ = {}
    for i in places:
        for j in range(i + 1, n):
            d = model.addVar(vtype=GRB.BINARY, name=f"differ[{i},{j}]")
            model.addConstr(d <= up[i] + up[j], name=f"xor_a[{i},{j}]")
            model.addConstr(d <= 2 - up[i] - up[j], name=f"xor_b[{i},{j}]")
            model.addConstr(d >= up[i] - up[j], name=f"xor_c[{i},{j}]")
            model.addConstr(d >= up[j] - up[i], name=f"xor_d[{i},{j}]")
            differ[i, j] = d

    # Periodic autocorrelation at shift s is the sum over i of sequence[i] * sequence[(i+s) mod n],
    # which is n - 2 * (the number of opposite-sign pairs). Shifts s and n - s use exactly the
    # same pairs, so they share one count and one table of squared values.
    energy_terms = []
    count_of = {}
    for s in range(1, n):
        rep = min(s, n - s)
        if rep not in count_of:
            opposite = gp.quicksum(differ[min(i, (i + rep) % n), max(i, (i + rep) % n)] for i in places)
            # pick[rep, k] is 1 when exactly k pairs have opposite signs; the square of the
            # autocorrelation (n - 2k)^2 is then a constant per choice of k, so the energy
            # stays linear.
            pick = model.addVars(range(n + 1), vtype=GRB.BINARY, name=f"pick[{rep}]")
            model.addConstr(pick.sum() == 1, name=f"one_count[{rep}]")
            model.addConstr(opposite == gp.quicksum(k * pick[k] for k in range(n + 1)), name=f"count[{rep}]")
            count_of[rep] = gp.quicksum((n - 2 * k) ** 2 * pick[k] for k in range(n + 1))
        energy_terms.append(count_of[rep])

    # Minimise the energy.
    model.setObjective(gp.quicksum(energy_terms), GRB.MINIMIZE)

    return model, {"sequence": sequence}
