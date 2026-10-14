"""Social golfers: schedule golfers into groups of equal size over several weeks so that no two golfers play together in a group more than once."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size
    golfers = range(n_golfers)
    weeks = range(n_weeks)
    groups = range(n_groups)

    model = gp.Model("social_golfers")

    # plays[g, w, k] is 1 when golfer g plays in group k in week w (one-hot form of assign[g][w]).
    plays = model.addVars(golfers, weeks, groups, vtype=GRB.BINARY, name="plays")
    for g in golfers:
        for w in weeks:
            model.addConstr(plays.sum(g, w, "*") == 1, name=f"one_group[{g},{w}]")
    assign = [[gp.quicksum(k * plays[g, w, k] for k in groups) for w in weeks] for g in golfers]

    # Each group has exactly group_size players in every week.
    for w in weeks:
        for k in groups:
            model.addConstr(plays.sum("*", w, k) == group_size, name=f"group_size[{w},{k}]")

    # Each pair of golfers meets at most once. They meet in week w when they are in the same
    # group; same[g1, g2, w] must be 1 then. Otherwise their group numbers differ, in one
    # direction or the other (higher says which), by at least 1; M = n_groups relaxes
    # the direction that does not hold.
    big = n_groups
    for g1 in golfers:
        for g2 in range(g1 + 1, n_golfers):
            met = []
            for w in weeks:
                same = model.addVar(vtype=GRB.BINARY, name=f"same[{g1},{g2},{w}]")
                higher = model.addVar(vtype=GRB.BINARY, name=f"higher[{g1},{g2},{w}]")
                model.addConstr(assign[g1][w] - assign[g2][w] + big * same - big * higher >= 1 - big,
                                name=f"apart_up[{g1},{g2},{w}]")
                model.addConstr(assign[g2][w] - assign[g1][w] + big * same + big * higher >= 1,
                                name=f"apart_down[{g1},{g2},{w}]")
                met.append(same)
            model.addConstr(gp.quicksum(met) <= 1, name=f"meet_once[{g1},{g2}]")

    return model, {"assign": assign}
