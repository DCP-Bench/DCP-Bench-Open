"""Kidney exchange: arrange compatible donations so that as many people as possible receive a kidney."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]  # compatible[i]: the people, 1-based, i can donate to
    people = range(n)

    model = gp.Model("kidney_exchange")

    # transplants[i, j] is 1 when person i donates to person j. A donation to
    # someone i is not compatible with gets an upper bound of 0.
    transplants = model.addVars(people, people, vtype=GRB.BINARY, name="transplants")
    for i in people:
        for j in people:
            if j + 1 not in compatible[i]:
                transplants[i, j].UB = 0

    for i in people:
        gives = transplants.sum(i, "*")
        receives = transplants.sum("*", i)
        # Each person donates at most once and receives at most once.
        model.addConstr(gives <= 1, name=f"donate_once[{i}]")
        model.addConstr(receives <= 1, name=f"receive_once[{i}]")
        # Anyone who gives a kidney receives one.
        model.addConstr(gives <= receives, name=f"gives_receives[{i}]")

    # Maximise the number of transplants.
    model.setObjective(transplants.sum(), GRB.MAXIMIZE)

    return model, {"transplants": [[transplants[i, j] for j in people] for i in people]}
