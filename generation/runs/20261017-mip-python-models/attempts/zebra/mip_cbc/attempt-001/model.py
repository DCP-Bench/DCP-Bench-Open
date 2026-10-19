# The Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0..4 from
# left to right. Each house has a colour, a nationality, a pet, a drink and a job,
# and every value of each category is used by exactly one house.
# The model has no instance data: the description fixes all sizes.
import mip

N = 5
CATEGORIES = {
    "colors": ["yellow", "green", "red", "white", "blue"],
    "nations": ["italy", "spain", "japan", "england", "norway"],
    "pets": ["cat", "zebra", "bear", "snails", "horse"],
    "drinks": ["milk", "water", "tea", "coffee", "juice"],
    "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
}


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Each value of each category gets a house. x[c][i][h] = 1 if value i of
    # category c is in house h. Every value takes exactly one house and every
    # house holds exactly one value of each category, so the houses are a
    # permutation for each category.
    x = {}
    pos = {}
    for c, values in CATEGORIES.items():
        x[c] = {}
        pos[c] = {}
        for i, name in enumerate(values):
            x[c][i] = [
                model.add_var(f"x_{c}_{name}_{h}", var_type=mip.BINARY)
                for h in range(N)
            ]
            model.add_constr(mip.xsum(x[c][i]) == 1, name=f"one_house_{c}_{name}")
            pos[c][i] = model.add_var(f"pos_{c}_{name}", lb=0, ub=N - 1, var_type=mip.INTEGER)
            model.add_constr(
                pos[c][i] == mip.xsum(h * x[c][i][h] for h in range(N)),
                name=f"pos_{c}_{name}_def",
            )
        for h in range(N):
            model.add_constr(
                mip.xsum(x[c][i][h] for i in range(N)) == 1,
                name=f"one_value_{c}_house_{h}",
            )

    def p(c, name):
        return pos[c][CATEGORIES[c].index(name)]

    def same_house(a, b, label):
        # the two values lie in the same house
        model.add_constr(a - b == 0, name=label)

    def left_of(a, b, label):
        # a is immediately on the left of b
        model.add_constr(a == b - 1, name=label)

    def next_to(a, b, label):
        # a and b are in neighbouring houses: |a - b| == 1, with binary s choosing the side
        s = model.add_var(f"s_{label}", var_type=mip.BINARY)
        model.add_constr(a - b == 2 * s - 1, name=label)

    # the painter owns the horse
    same_house(p("jobs", "painter"), p("pets", "horse"), "painter_owns_horse")
    # the diplomat drinks coffee
    same_house(p("jobs", "diplomat"), p("drinks", "coffee"), "diplomat_drinks_coffee")
    # the one who drinks milk lives in the white house
    same_house(p("drinks", "milk"), p("colors", "white"), "milk_in_white_house")
    # the Spaniard is a painter
    same_house(p("nations", "spain"), p("jobs", "painter"), "spaniard_is_painter")
    # the Englishman lives in the red house
    same_house(p("nations", "england"), p("colors", "red"), "englishman_in_red_house")
    # the snails are owned by the sculptor
    same_house(p("pets", "snails"), p("jobs", "sculptor"), "snails_owned_by_sculptor")
    # the green house is immediately on the left of the red one
    left_of(p("colors", "green"), p("colors", "red"), "green_left_of_red")
    # the Norwegian lives immediately on the right of the blue house
    left_of(p("colors", "blue"), p("nations", "norway"), "norwegian_right_of_blue")
    # the doctor drinks milk
    same_house(p("jobs", "doctor"), p("drinks", "milk"), "doctor_drinks_milk")
    # the diplomat is Japanese
    same_house(p("jobs", "diplomat"), p("nations", "japan"), "diplomat_is_japanese")
    # the Norwegian owns the zebra
    same_house(p("nations", "norway"), p("pets", "zebra"), "norwegian_owns_zebra")
    # the green house is next to the white one
    next_to(p("colors", "green"), p("colors", "white"), "green_next_to_white")
    # the horse is owned by the neighbor of the diplomat
    next_to(p("pets", "horse"), p("jobs", "diplomat"), "horse_owner_neighbor_of_diplomat")

    # the Italian either lives in the red, white or green house
    t = {
        k: model.add_var(f"t_italian_{k}", var_type=mip.BINARY)
        for k in ["red", "white", "green"]
    }
    model.add_constr(mip.xsum(t.values()) == 1, name="italian_one_of_three_houses")
    for k in ["red", "white", "green"]:
        model.add_constr(
            p("nations", "italy") - p("colors", k) <= (N - 1) * (1 - t[k]),
            name=f"italian_in_{k}_upper",
        )
        model.add_constr(
            p("colors", k) - p("nations", "italy") <= (N - 1) * (1 - t[k]),
            name=f"italian_in_{k}_lower",
        )

    outputs = {
        "colors": [pos["colors"][i] for i in range(N)],
        "drinks": [pos["drinks"][i] for i in range(N)],
        "jobs": [pos["jobs"][i] for i in range(N)],
        "nations": [pos["nations"][i] for i in range(N)],
        "pets": [pos["pets"][i] for i in range(N)],
    }
    return model, outputs
