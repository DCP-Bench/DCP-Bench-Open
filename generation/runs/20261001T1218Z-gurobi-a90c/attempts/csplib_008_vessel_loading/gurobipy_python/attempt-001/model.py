"""Vessel loading: place rectangular containers on a deck, each either way round, without overlap and with the required separation between classes."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    width = instance["width"]            # per container
    length = instance["length"]          # per container
    classes = instance["classes"]        # per container: its class, numbered from 1
    separation = instance["separation"]  # [class][class]: required gap between containers of those classes
    containers = range(instance["n_containers"])

    model = gp.Model("vessel_loading")

    # Each container occupies the rectangle left..right by bottom..top on the deck.
    left = model.addVars(containers, lb=0, ub=deck_width, vtype=GRB.INTEGER, name="left")
    right = model.addVars(containers, lb=0, ub=deck_width, vtype=GRB.INTEGER, name="right")
    bottom = model.addVars(containers, lb=0, ub=deck_length, vtype=GRB.INTEGER, name="bottom")
    top = model.addVars(containers, lb=0, ub=deck_length, vtype=GRB.INTEGER, name="top")

    # A container lies lengthways or turned: turned[i] is 1 when its width runs along the deck's
    # length axis. Either way the rectangle is width x length or length x width, so the two
    # extents are linear in turned[i].
    turned = model.addVars(containers, vtype=GRB.BINARY, name="turned")
    for i in containers:
        model.addConstr(right[i] - left[i] == width[i] + (length[i] - width[i]) * turned[i],
                        name=f"extent_x[{i}]")
        model.addConstr(top[i] - bottom[i] == length[i] + (width[i] - length[i]) * turned[i],
                        name=f"extent_y[{i}]")

    # No overlap: for each pair, one container is at least `sep` to the left of, right of, below
    # or above the other, where sep is the separation required between their classes. A branch
    # that does not hold is relaxed by a big-M: the deck extent along that axis plus sep, which
    # is the most its left side can exceed its right side by.
    for a in containers:
        for b in range(a + 1, len(width)):
            sep = separation[classes[a] - 1][classes[b] - 1]
            big_x = deck_width + sep
            big_y = deck_length + sep
            branch = model.addVars(4, vtype=GRB.BINARY, name=f"branch[{a},{b}]")
            model.addConstr(right[a] + sep <= left[b] + big_x * (1 - branch[0]), name=f"a_left_of_b[{a},{b}]")
            model.addConstr(left[a] >= right[b] + sep - big_x * (1 - branch[1]), name=f"a_right_of_b[{a},{b}]")
            model.addConstr(top[a] + sep <= bottom[b] + big_y * (1 - branch[2]), name=f"a_below_b[{a},{b}]")
            model.addConstr(bottom[a] >= top[b] + sep - big_y * (1 - branch[3]), name=f"a_above_b[{a},{b}]")
            model.addConstr(branch.sum() >= 1, name=f"separate[{a},{b}]")

    return model, {
        "left": [left[i] for i in containers],
        "right": [right[i] for i in containers],
        "top": [top[i] for i in containers],
        "bottom": [bottom[i] for i in containers],
    }
