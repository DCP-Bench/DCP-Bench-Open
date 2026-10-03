"""Allergy: four friends (Debra, Janet, Hugh, Rick) are each allergic to a different one of
eggs, mold, nuts and ragweed, and each has a different surname of Baxter, Lemon, Malone and
Fleet. Match surnames and allergies to the friends from the clues.

The model reports, for each food and each surname, the friend it belongs to
(Debra = 0, Janet = 1, Hugh = 2, Rick = 3).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its names are below

    friends = Debra, Janet, Hugh, Rick = list(range(4))
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    problem = pulp.LpProblem("allergy", pulp.LpMinimize)  # satisfaction

    # food[f][p] = 1 if friend p is allergic to food f; surname[s][p] = 1 if friend p has
    # surname s. Each is a one-to-one matching, which states the all-different.
    food = {f: [pulp.LpVariable(f"food_{f}_{p}", cat="Binary") for p in friends] for f in foods}
    surname = {s: [pulp.LpVariable(f"surname_{s}_{p}", cat="Binary") for p in friends]
               for s in surnames}
    for matching, keys in ((food, foods), (surname, surnames)):
        # each food (surname) belongs to one friend
        for key in keys:
            problem += pulp.lpSum(matching[key]) == 1
        # each friend has one food (surname): everyone's is different
        for p in friends:
            problem += pulp.lpSum(matching[key][p] for key in keys) == 1

    # Rick is not allergic to mold
    problem += food["mold"][Rick] == 0
    # Baxter is allergic to eggs
    for p in friends:
        problem += food["eggs"][p] == surname["baxter"][p]
    # Hugh is neither surnamed Lemon nor Fleet
    problem += surname["lemon"][Hugh] == 0
    problem += surname["fleet"][Hugh] == 0
    # Debra is allergic to ragweed
    problem += food["ragweed"][Debra] == 1
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    problem += surname["lemon"][Janet] == 0
    problem += food["eggs"][Janet] == 0
    problem += food["mold"][Janet] == 0

    # the friend each food and surname belongs to
    outputs = {f: pulp.lpSum(p * food[f][p] for p in friends) for f in foods}
    outputs.update({s: pulp.lpSum(p * surname[s][p] for p in friends) for s in surnames})
    return problem, outputs
