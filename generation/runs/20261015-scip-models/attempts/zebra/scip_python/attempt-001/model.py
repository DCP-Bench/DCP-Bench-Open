# Zebra puzzle: five houses in a row, each with a different colour, nationality, pet,
# drink and job; the clues fix which attribute goes with which, and the question is which
# house owns the zebra and which drinks water. Output: for every attribute value, the
# house number (0 = leftmost, 4 = rightmost) it is found in.
from pyscipopt import Model, quicksum

HOUSES = range(5)
ATTRIBUTES = {
    "colors": ["yellow", "green", "red", "white", "blue"],
    "nations": ["italy", "spain", "japan", "england", "norway"],
    "pets": ["cat", "zebra", "bear", "snails", "horse"],
    "drinks": ["milk", "water", "tea", "coffee", "juice"],
    "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
}


def build(instance):
    m = Model("zebra")

    # x[a, v, h] = 1 if value v of attribute a is in house h
    x = {}
    for a, values in ATTRIBUTES.items():
        for v in values:
            for h in HOUSES:
                x[a, v, h] = m.addVar(name=f"{a}_{v}_{h}", vtype="B")
    # every value sits in exactly one house, and every house holds exactly one value per attribute
    for a, values in ATTRIBUTES.items():
        for v in values:
            m.addCons(quicksum(x[a, v, h] for h in HOUSES) == 1)
        for h in HOUSES:
            m.addCons(quicksum(x[a, v, h] for v in values) == 1)

    # the house number of each value
    pos = {(a, v): quicksum(h * x[a, v, h] for h in HOUSES)
           for a, values in ATTRIBUTES.items() for v in values}

    def P(a, v):
        return pos[a, v]

    # the painter owns the horse
    m.addCons(P("jobs", "painter") == P("pets", "horse"))
    # the diplomat drinks coffee
    m.addCons(P("jobs", "diplomat") == P("drinks", "coffee"))
    # the one who drinks milk lives in the white house
    m.addCons(P("drinks", "milk") == P("colors", "white"))
    # the Spaniard is a painter
    m.addCons(P("nations", "spain") == P("jobs", "painter"))
    # the Englishman lives in the red house
    m.addCons(P("nations", "england") == P("colors", "red"))
    # the snails are owned by the sculptor
    m.addCons(P("pets", "snails") == P("jobs", "sculptor"))
    # the green house is immediately on the left of the red one
    m.addCons(P("colors", "red") == P("colors", "green") + 1)
    # the Norwegian lives immediately on the right of the blue house
    m.addCons(P("nations", "norway") == P("colors", "blue") + 1)
    # the doctor drinks milk
    m.addCons(P("jobs", "doctor") == P("drinks", "milk"))
    # the diplomat is Japanese
    m.addCons(P("jobs", "diplomat") == P("nations", "japan"))
    # the Norwegian owns the zebra
    m.addCons(P("nations", "norway") == P("pets", "zebra"))
    # the green house is next to the white one
    m.addCons(abs(P("colors", "green") - P("colors", "white")) == 1)
    # the horse is owned by the neighbour of the diplomat
    m.addCons(abs(P("pets", "horse") - P("jobs", "diplomat")) == 1)
    # the Italian lives in the red, white or green house, so not in the blue or yellow house
    for h in HOUSES:
        m.addCons(x["nations", "italy", h] + x["colors", "blue", h] + x["colors", "yellow", h] <= 1)

    outputs = {
        a: [P(a, v) for v in values] for a, values in ATTRIBUTES.items()
    }
    return m, outputs
