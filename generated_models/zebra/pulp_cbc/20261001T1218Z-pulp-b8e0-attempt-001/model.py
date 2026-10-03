"""Zebra (Einstein's puzzle): five houses in a row, each with a different colour, nationality,
pet, drink and job. From the clues, find which house each belongs to.

The model reports, for each colour, nation, job, pet and drink, its house 0..4 (left to
right).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    n = 5
    houses = range(n)
    groups = {
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
    }

    problem = pulp.LpProblem("zebra", pulp.LpMinimize)  # satisfaction

    # at[item][h] = 1 if the colour, nation, job, pet or drink belongs to house h; within a
    # group every item has a different house
    at = {item: [pulp.LpVariable(f"at_{item}_{h}", cat="Binary") for h in houses]
          for items in groups.values() for item in items}
    for items in groups.values():
        for item in items:
            problem += pulp.lpSum(at[item]) == 1
        for h in houses:
            problem += pulp.lpSum(at[item][h] for item in items) == 1

    def same(x, y):
        """x and y belong to the same house"""
        for h in houses:
            problem.addConstraint(at[x][h] == at[y][h])

    def right_of(x, y):
        """x is in the house immediately to the right of y's"""
        problem.addConstraint(at[x][0] == 0)
        for h in houses:
            if h + 1 < n:
                problem.addConstraint(at[x][h + 1] == at[y][h])

    def next_to(x, y):
        """x is in a house next to y's: if x is in house h, y is in house h - 1 or h + 1"""
        for h in houses:
            problem.addConstraint(at[x][h] <= pulp.lpSum(at[y][g] for g in (h - 1, h + 1)
                                                         if 0 <= g < n))

    same("painter", "horse")       # the painter owns the horse
    same("diplomat", "coffee")     # the diplomat drinks coffee
    same("white", "milk")          # the one who drinks milk lives in the white house
    same("spain", "painter")       # the Spaniard is a painter
    same("england", "red")         # the Englishman lives in the red house
    same("snails", "sculptor")     # the snails are owned by the sculptor
    right_of("red", "green")       # the green house is immediately left of the red one
    right_of("norway", "blue")     # the Norwegian lives immediately right of the blue house
    same("doctor", "milk")         # the doctor drinks milk
    same("japan", "diplomat")      # the diplomat is Japanese
    same("norway", "zebra")        # the Norwegian owns the zebra
    next_to("green", "white")      # the green house is next to the white one
    next_to("horse", "diplomat")   # the horse is owned by the neighbour of the diplomat
    # the Italian lives in the red, white or green house
    for h in houses:
        problem += at["italy"][h] <= at["red"][h] + at["white"][h] + at["green"][h]

    return problem, {key: [pulp.lpSum(h * var for h, var in enumerate(at[item])) for item in items]
                     for key, items in groups.items()}
