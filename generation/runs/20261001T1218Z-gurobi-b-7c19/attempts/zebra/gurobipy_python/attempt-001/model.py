"""Zebra puzzle: place five colours, nations, jobs, pets and drinks in five houses in a row."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. Houses are numbered 0..4 from the left.
HOUSES = range(5)
CATEGORIES = {
    "colors": ["yellow", "green", "red", "white", "blue"],
    "nations": ["italy", "spain", "japan", "england", "norway"],
    "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
    "pets": ["cat", "zebra", "bear", "snails", "horse"],
    "drinks": ["milk", "water", "tea", "coffee", "juice"],
}


def build(instance):
    model = gp.Model("zebra")

    # at[item, h] = 1 when the item belongs to house h. Within a category
    # every house has a different item.
    at = {}
    for items in CATEGORIES.values():
        for item in items:
            for h in HOUSES:
                at[item, h] = model.addVar(vtype=GRB.BINARY, name=f"at[{item},{h}]")
            model.addConstr(gp.quicksum(at[item, h] for h in HOUSES) == 1, name=f"placed[{item}]")
        for h in HOUSES:
            model.addConstr(gp.quicksum(at[item, h] for item in items) == 1, name=f"different[{items[0]},{h}]")

    def house(item):
        return gp.quicksum(h * at[item, h] for h in HOUSES)

    def same(x, y):
        for h in HOUSES:
            model.addConstr(at[x, h] == at[y, h], name=f"{x}_with_{y}[{h}]")

    def next_to(x, y):
        """x lives in a house adjacent to y's."""
        for h in HOUSES:
            beside = [at[y, k] for k in (h - 1, h + 1) if k in HOUSES]
            model.addConstr(at[x, h] <= gp.quicksum(beside), name=f"{x}_next_to_{y}[{h}]")

    same("painter", "horse")            # the painter owns the horse
    same("diplomat", "coffee")          # the diplomat drinks coffee
    same("white", "milk")               # the one who drinks milk lives in the white house
    same("spain", "painter")            # the Spaniard is a painter
    same("england", "red")              # the Englishman lives in the red house
    same("snails", "sculptor")          # the snails are owned by the sculptor
    # the green house is immediately on the left of the red one
    model.addConstr(house("green") + 1 == house("red"), name="green_left_of_red")
    # the Norwegian lives immediately on the right of the blue house
    model.addConstr(house("blue") + 1 == house("norway"), name="norway_right_of_blue")
    same("doctor", "milk")              # the doctor drinks milk
    same("japan", "diplomat")           # the diplomat is Japanese
    same("norway", "zebra")             # the Norwegian owns the zebra
    next_to("green", "white")           # the green house is next to the white one
    next_to("horse", "diplomat")        # the horse is owned by the neighbour of the diplomat
    # the Italian lives in the red, white or green house
    for h in HOUSES:
        model.addConstr(at["italy", h] <= at["red", h] + at["white", h] + at["green", h], name=f"italy[{h}]")

    return model, {name: [house(item) for item in items] for name, items in CATEGORIES.items()}
