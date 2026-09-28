"""Fifty puzzle: knock over dummies whose numbers add up to exactly the target sum."""
from docplex.mp.model import Model


def build(instance):
    values = instance["values"]

    model = Model("fifty_puzzle")

    # dummies[i] is 1 when dummy i is knocked over.
    dummies = model.binary_var_list(len(values), name="dummies")

    # The numbers on the knocked-over dummies add up to the target, neither more nor less.
    model.add_constraint(model.dot(dummies, values) == instance["target_sum"], ctname="target")

    return model, {"dummies": dummies}
