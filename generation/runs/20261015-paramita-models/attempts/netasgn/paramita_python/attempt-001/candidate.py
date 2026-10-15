# Project assignment problem (netasgn): assign hours from people to projects
# at minimum total cost, meeting each person's supply, each project's demand
# and the per-cell limits. Each hour count x[i][j] is encoded in unary: the
# Bool x_i_j_ge_k means "x[i][j] >= k", so the value is the number of true bits.
from paramita.modelling import Bool, If


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    n_people = len(supply)
    n_projects = len(demand)

    cons = []

    # unary bits: x[i][j] = sum of bits, bounded by the cell limit Limit_ij
    bits = [[[Bool(f"x_{i}_{j}_ge_{k}") for k in range(1, limit[i][j] + 1)]
             for j in range(n_projects)]
            for i in range(n_people)]
    # the bits of one cell are ordered: x >= k+1 implies x >= k
    for i in range(n_people):
        for j in range(n_projects):
            for k in range(len(bits[i][j]) - 1):
                cons.append(If(bits[i][j][k + 1], bits[i][j][k]))

    def value(i, j):
        return sum(bits[i][j])

    def total(terms):
        # Paramita needs an expression; an empty sum is the constant 0.
        return sum(terms) if terms else 0

    def equal_to(terms, k):
        # Bool-free integer sums cannot be compared when empty, so an empty
        # sum must equal k only when k is 0; otherwise the model is infeasible.
        if terms:
            return sum(terms) == k
        if k == 0:
            return None
        fresh = Bool("no_hours_available")
        return fresh & ~fresh

    # the total hours assigned from each person i equals its supply
    for i in range(n_people):
        terms = [b for j in range(n_projects) for b in bits[i][j]]
        c = equal_to(terms, supply[i])
        if c is not None:
            cons.append(c)

    # the total hours assigned to each project j equals its demand
    for j in range(n_projects):
        terms = [b for i in range(n_people) for b in bits[i][j]]
        c = equal_to(terms, demand[j])
        if c is not None:
            cons.append(c)

    assign = [[value(i, j) for j in range(n_projects)] for i in range(n_people)]

    # the total cost of the assignment: sum of Cost_ij times the hours x_ij
    total_cost = total([cost[i][j] * b
                        for i in range(n_people)
                        for j in range(n_projects)
                        for b in bits[i][j]])

    return cons, {"assign": assign, "total_cost": total_cost}, ("minimize", total_cost)
