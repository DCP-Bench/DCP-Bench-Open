# Zebra puzzle (Einstein's puzzle). Five houses in a row, numbered 0 (left) to 4
# (right). Each house has one colour, one nationality, one pet, one drink and one
# job, all different within their attribute. The clues below are the problem's
# own statements. The puzzle has no instance data; the instance argument is unused.
from paramita.modelling import Bool, If, Or

COLORS = ["yellow", "green", "red", "white", "blue"]
NATIONS = ["italy", "spain", "japan", "england", "norway"]
PETS = ["cat", "zebra", "bear", "snails", "horse"]
DRINKS = ["milk", "water", "tea", "coffee", "juice"]
JOBS = ["painter", "sculptor", "diplomat", "pianist", "doctor"]
ATTRIBUTES = {
    "color": COLORS,
    "nation": NATIONS,
    "pet": PETS,
    "drink": DRINKS,
    "job": JOBS,
}
HOUSES = range(5)


def build(instance):
    # one-hot: H[attr][value][house] is true when that value is in that house
    H = {
        a: {v: [Bool(f"{a}_{v}_in_house_{h}") for h in HOUSES] for v in vals}
        for a, vals in ATTRIBUTES.items()
    }
    cons = []

    # each value of each attribute is in exactly one house
    for a, vals in ATTRIBUTES.items():
        for v in vals:
            cons.append(sum(H[a][v]) == 1)

    # each house holds exactly one value of each attribute
    for a, vals in ATTRIBUTES.items():
        for h in HOUSES:
            cons.append(sum(H[a][v][h] for v in vals) == 1)

    # house number of each value, as an integer expression
    P = {a: {v: sum(h * H[a][v][h] for h in HOUSES) for v in vals}
         for a, vals in ATTRIBUTES.items()}

    # the painter owns the horse
    cons.append(P["job"]["painter"] == P["pet"]["horse"])

    # the diplomat drinks coffee
    cons.append(P["job"]["diplomat"] == P["drink"]["coffee"])

    # the one who drinks milk lives in the white house
    cons.append(P["drink"]["milk"] == P["color"]["white"])

    # the Spaniard is a painter
    cons.append(P["nation"]["spain"] == P["job"]["painter"])

    # the Englishman lives in the red house
    cons.append(P["nation"]["england"] == P["color"]["red"])

    # the snails are owned by the sculptor
    cons.append(P["pet"]["snails"] == P["job"]["sculptor"])

    # the green house is immediately on the left of the red one
    cons.append(P["color"]["green"] + 1 == P["color"]["red"])

    # the Norwegian lives immediately on the right of the blue house
    cons.append(P["nation"]["norway"] == P["color"]["blue"] + 1)

    # the doctor drinks milk
    cons.append(P["job"]["doctor"] == P["drink"]["milk"])

    # the diplomat is Japanese
    cons.append(P["job"]["diplomat"] == P["nation"]["japan"])

    # the Norwegian owns the zebra
    cons.append(P["nation"]["norway"] == P["pet"]["zebra"])

    # the green house is next to the white one
    cons.append(Or([P["color"]["green"] + 1 == P["color"]["white"],
                    P["color"]["white"] + 1 == P["color"]["green"]]))

    # the horse is owned by the neighbour of the diplomat
    cons.append(Or([P["pet"]["horse"] + 1 == P["job"]["diplomat"],
                    P["job"]["diplomat"] + 1 == P["pet"]["horse"]]))

    # the Italian lives in the red, white or green house
    cons.append(Or([P["nation"]["italy"] == P["color"]["red"],
                    P["nation"]["italy"] == P["color"]["white"],
                    P["nation"]["italy"] == P["color"]["green"]]))

    outputs = {a: [P[a][v] for v in vals] for a, vals in ATTRIBUTES.items()}
    outputs = {
        "colors": outputs["color"],
        "nations": outputs["nation"],
        "pets": outputs["pet"],
        "drinks": outputs["drink"],
        "jobs": outputs["job"],
    }
    return cons, outputs
