"""Zebra puzzle: five houses in a row, each with a different colour, nationality, pet, drink
and job. Place everything from the clues; houses are numbered 0..4 from the left.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the items and clues are from the statement.
    n_houses = 5
    houses = range(n_houses)
    groups = {
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
    }

    model = Model("zebra")

    # at[e, h] is 1 when item e belongs to house h. Within a group every item is in one house
    # and no two items share one (all different).
    at = {}
    for items in groups.values():
        for e in items:
            for h in houses:
                at[e, h] = model.binary_var(name=f"{e}_in_{h}")
            model.add_constraint(model.sum(at[e, h] for h in houses) == 1)
        for h in houses:
            model.add_constraint(model.sum(at[e, h] for e in items) == 1)

    def house(e):
        return model.sum(h * at[e, h] for h in houses if h)

    def same_house(a, b):
        for h in houses:
            model.add_constraint(at[a, h] == at[b, h])

    def next_to(a, b):
        # a lives immediately left or right of b.
        for h in houses:
            model.add_constraint(at[a, h] <= model.sum(at[b, k] for k in (h - 1, h + 1)
                                                       if 0 <= k < n_houses))

    same_house("painter", "horse")       # the painter owns the horse
    same_house("diplomat", "coffee")     # the diplomat drinks coffee
    same_house("white", "milk")          # the milk drinker lives in the white house
    same_house("spain", "painter")       # the Spaniard is a painter
    same_house("england", "red")         # the Englishman lives in the red house
    same_house("snails", "sculptor")     # the sculptor owns the snails
    # The green house is immediately left of the red one.
    model.add_constraint(house("green") + 1 == house("red"))
    # The Norwegian lives immediately right of the blue house.
    model.add_constraint(house("blue") + 1 == house("norway"))
    same_house("doctor", "milk")         # the doctor drinks milk
    same_house("japan", "diplomat")      # the diplomat is Japanese
    same_house("norway", "zebra")        # the Norwegian owns the zebra
    next_to("green", "white")            # the green house is next to the white one
    next_to("horse", "diplomat")         # the horse is owned by the diplomat's neighbour
    # The Italian lives in the red, white or green house (three different houses).
    for h in houses:
        model.add_constraint(at["italy", h] <= at["red", h] + at["white", h] + at["green", h])

    outputs = {name: [house(e) for e in items] for name, items in groups.items()}
    return model, outputs
