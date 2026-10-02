# Zebra puzzle: five houses in a row, each with a colour, an inhabitant of some nationality, a job,
# a pet and a drink, all different within each kind. Clues relate them; find the house number
# (0..4, left to right) of every colour, nationality, job, pet and drink.
from exact import Exact


def build(instance):
    # This problem has no instance data. The five houses and the five items of each kind belong to
    # the problem statement.
    n_houses = 5
    kinds = {
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
    }

    solver = Exact()

    # Each item is a variable holding the house it belongs to. Comparing "which house" with other
    # items needs 0/1 indicators, so is_in[item][h] = 1 when the item is in house h.
    is_in = {}
    for items in kinds.values():
        for item in items:
            solver.addVariable(item, 0, n_houses - 1)
            is_in[item] = [f"{item}_in_{h}" for h in range(n_houses)]
            for indicator in is_in[item]:
                solver.addVariable(indicator, 0, 1)
            # the item is in exactly one house, and the indicators give its number
            solver.addConstraint([(1, indicator) for indicator in is_in[item]], True, 1, True, 1)
            solver.addConstraint([(h, is_in[item][h]) for h in range(1, n_houses)] +
                                 [(-1, item)], True, 0, True, 0)
        # All items of one kind are in different houses: every house holds exactly one of them.
        for h in range(n_houses):
            solver.addConstraint([(1, is_in[item][h]) for item in items], True, 1, True, 1)

    def same_house(x, y):
        solver.addConstraint([(1, x), (-1, y)], True, 0, True, 0)

    def immediately_left(x, y):
        # x is in the house directly to the left of y's house
        solver.addConstraint([(1, x), (-1, y)], True, -1, True, -1)

    def neighbours(x, y):
        # x and y are in adjacent houses: for every house h, if x is in h then y is in h-1 or h+1
        for h in range(n_houses):
            next_door = [(1, is_in[y][g]) for g in (h - 1, h + 1) if 0 <= g < n_houses]
            solver.addConstraint(next_door + [(-1, is_in[x][h])], True, 0)

    # the painter owns the horse
    same_house("painter", "horse")
    # the diplomat drinks coffee
    same_house("diplomat", "coffee")
    # the one who drinks milk lives in the white house
    same_house("milk", "white")
    # the Spaniard is a painter
    same_house("spain", "painter")
    # the Englishman lives in the red house
    same_house("england", "red")
    # the snails are owned by the sculptor
    same_house("snails", "sculptor")
    # the green house is immediately on the left of the red one
    immediately_left("green", "red")
    # the Norwegian lives immediately on the right of the blue house
    immediately_left("blue", "norway")
    # the doctor drinks milk
    same_house("doctor", "milk")
    # the diplomat is Japanese
    same_house("japan", "diplomat")
    # the Norwegian owns the zebra
    same_house("norway", "zebra")
    # the green house is next to the white one
    neighbours("green", "white")
    # the horse is owned by the neighbor of the diplomat
    neighbours("horse", "diplomat")
    # the Italian either lives in the red, white or green house
    for h in range(n_houses):
        solver.addConstraint([(1, is_in[c][h]) for c in ("red", "white", "green")] +
                             [(-1, is_in["italy"][h])], True, 0)

    return solver, {kind: items for kind, items in kinds.items()}
