# Four islands: Pwana, Quero, Rayou and Skern each have a different primary export
# (alabaster, bananas, coconuts, durian fruit) and a different tourist attraction
# (resort hotel, ice skating rink, jai alai stadium, koala preserve). The map is a
# 2x2 grid with positions A=0, B=1, C=2, D=3: A-B and C-D are east-west bridges,
# A-C and B-D are north-south bridges, and no other pair of islands is connected.
import mip

# For a position p, the positions due south, east or west of p.
SOUTH = {0: [2], 1: [3]}
EAST = {0: [1], 2: [3]}
WEST = {1: [0], 3: [2]}
# For a position p, the positions joined to p by a bridge.
EW_BRIDGE = {0: [1], 1: [0], 2: [3], 3: [2]}
NS_BRIDGE = {0: [2], 2: [0], 1: [3], 3: [1]}
ADJACENT = {0: [1, 2], 1: [0, 3], 2: [0, 3], 3: [1, 2]}


def one_hot_group(model, tag):
    # x[k][p] = 1 when item k is at map position p; each item and each position used once
    x = [[model.add_var(f"{tag}_{k}_{p}", var_type=mip.BINARY) for p in range(4)]
         for k in range(4)]
    for k in range(4):
        model.add_constr(mip.xsum(x[k]) == 1)
    for p in range(4):
        model.add_constr(mip.xsum([x[k][p] for k in range(4)]) == 1)
    return x


def related(model, xs, ys, mapping):
    # the item xs sits at a position listed in mapping for the position of the item ys
    for p in range(4):
        model.add_constr(mip.xsum([ys[p]]) <= mip.xsum([xs[q] for q in mapping.get(p, [])]))


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # isl[i][p]: island i (Pwana, Quero, Rayou, Skern) sits at position p
    # exp[k][p]: the island at position p exports k (alabaster, bananas, coconuts, durian)
    # att[k][p]: the island at position p has attraction k (hotel, rink, jai alai, koala)
    isl = one_hot_group(model, "isl")
    exp = one_hot_group(model, "exp")
    att = one_hot_group(model, "att")

    # Pwana (0), Quero (1), Rayou (2), Skern (3)
    island = [model.add_var(f"island_{i}", lb=0, ub=3, var_type=mip.INTEGER) for i in range(4)]
    # alabaster (0), bananas (1), coconuts (2), durian fruit (3)
    export = [model.add_var(f"export_{k}", lb=0, ub=3, var_type=mip.INTEGER) for k in range(4)]
    # resort hotel (0), ice skating rink (1), jai alai stadium (2), koala preserve (3)
    attraction = [model.add_var(f"attraction_{k}", lb=0, ub=3, var_type=mip.INTEGER)
                  for k in range(4)]
    for i in range(4):
        model.add_constr(island[i] == mip.xsum([p * isl[i][p] for p in range(4)]))
    for k in range(4):
        model.add_constr(export[k] == mip.xsum([p * exp[k][p] for p in range(4)]))
        model.add_constr(attraction[k] == mip.xsum([p * att[k][p] for p in range(4)]))

    # The island noted for its koala preserve is due south of Pwana.
    related(model, att[3], isl[0], SOUTH)

    # The island with the largest alabaster quarry is due west of Quero.
    related(model, exp[0], isl[1], WEST)

    # The island with the resort hotel is due east of the one that exports durian fruit.
    related(model, att[0], exp[3], EAST)

    # Skern and the island with the jai alai stadium are connected by a north-south bridge.
    related(model, att[2], isl[3], NS_BRIDGE)

    # Rayou and the island that exports bananas are connected by an east-west bridge.
    related(model, exp[1], isl[2], EW_BRIDGE)

    # The islands noted for the South Pacific's largest ice skating rink and for the
    # jai alai stadium are not connected by a bridge.
    for p in range(4):
        for q in ADJACENT[p]:
            model.add_constr(att[1][p] + att[2][q] <= 1)

    outputs = {"island": island, "export": export, "attraction": attraction}
    return model, outputs
