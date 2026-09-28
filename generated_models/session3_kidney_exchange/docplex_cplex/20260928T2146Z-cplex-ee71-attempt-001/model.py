"""Kidney exchange: arrange compatible donations so that as many people as possible receive a kidney."""
from docplex.mp.model import Model


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]  # compatible[i]: the people, 1-based, i can donate to
    people = range(n)

    model = Model("kidney_exchange")

    # transplants[i, j] is 1 when person i donates to person j. A donation to
    # someone i is not compatible with gets an upper bound of 0.
    transplants = model.binary_var_matrix(people, people, name="transplants")
    for i in people:
        for j in people:
            if j + 1 not in compatible[i]:
                transplants[i, j].ub = 0

    for i in people:
        gives = model.sum(transplants[i, j] for j in people)
        receives = model.sum(transplants[j, i] for j in people)
        # Each person donates at most once and receives at most once.
        model.add_constraint(gives <= 1, ctname=f"donate_once_{i}")
        model.add_constraint(receives <= 1, ctname=f"receive_once_{i}")
        # Anyone who gives a kidney receives one.
        model.add_constraint(gives <= receives, ctname=f"gives_receives_{i}")

    # Maximise the number of transplants.
    model.maximize(model.sum(transplants.values()))

    return model, {"transplants": [[transplants[i, j] for j in people] for i in people]}
