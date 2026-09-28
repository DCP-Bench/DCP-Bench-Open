"""Archery puzzle: choose how often to hit each target so that the score comes as close as possible to the target score."""
from docplex.mp.model import Model


def build(instance):
    targets = instance["targets"]  # points for a hit on each target
    goal = instance["target_score"]

    model = Model("archery_puzzle")

    # hits[i] is how many arrows hit target i; the reference model allows 0..goal.
    hits = model.integer_var_list(len(targets), 0, goal, name="hits")

    # score is the points scored, which the reference model bounds to 0..2 * goal.
    score = model.integer_var(0, 2 * goal, name="score")
    model.add_constraint(score == model.dot(hits, targets), ctname="score")

    # deviation is how far the score is from the goal. Two lower bounds suffice
    # because deviation is minimised: at the optimum it equals |goal - score|.
    deviation = model.integer_var(0, 2 * goal, name="deviation")
    model.add_constraint(deviation >= goal - score, ctname="below_goal")
    model.add_constraint(deviation >= score - goal, ctname="above_goal")

    # Come as close to the goal as possible.
    model.minimize(deviation)

    return model, {"hits": hits}
