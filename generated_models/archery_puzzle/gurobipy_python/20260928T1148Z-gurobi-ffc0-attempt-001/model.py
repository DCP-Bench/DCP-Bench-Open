"""Archery puzzle: choose how often to hit each target so that the score comes as close as possible to the target score."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    targets = instance["targets"]  # points for a hit on each target
    goal = instance["target_score"]
    rings = range(len(targets))

    model = gp.Model("archery_puzzle")

    # hits[i] is how many arrows hit target i; the reference model allows 0..goal.
    hits = model.addVars(rings, lb=0, ub=goal, vtype=GRB.INTEGER, name="hits")

    # score is the points scored, which the reference model bounds to 0..2 * goal.
    score = model.addVar(lb=0, ub=2 * goal, vtype=GRB.INTEGER, name="score")
    model.addConstr(score == gp.quicksum(targets[i] * hits[i] for i in rings), name="score")

    # deviation is how far the score is from the goal. Two lower bounds suffice
    # because deviation is minimised: at the optimum it equals |goal - score|.
    deviation = model.addVar(lb=0, ub=2 * goal, vtype=GRB.INTEGER, name="deviation")
    model.addConstr(deviation >= goal - score, name="below_goal")
    model.addConstr(deviation >= score - goal, name="above_goal")

    # Come as close to the goal as possible.
    model.setObjective(deviation, GRB.MINIMIZE)

    return model, {"hits": [hits[i] for i in rings]}
