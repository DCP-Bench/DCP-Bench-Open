"""Four islands: four islands joined by bridges in a square, A-B on top and C-D below, each
with a different name, export and tourist attraction. Place every name, export and
attraction on the map from six clues.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Map positions: A = 0 (north-west), B = 1
    # (north-east), C = 2 (south-west), D = 3 (south-east).
    n = 4
    A, B, C, D = range(n)
    positions = range(n)

    model = Model("four_islands")

    def placed(names):
        # at[k, p] is 1 when item k sits at map position p; within the group every item has
        # one position and no two share one (all different).
        at = {(k, p): model.binary_var(name=f"{names[k]}_at_{p}") for k in range(n)
              for p in positions}
        for k in range(n):
            model.add_constraint(model.sum(at[k, p] for p in positions) == 1)
        for p in positions:
            model.add_constraint(model.sum(at[k, p] for k in range(n)) == 1)
        where = [model.integer_var(0, n - 1, name=names[k]) for k in range(n)]
        for k in range(n):
            model.add_constraint(where[k] == model.sum(p * at[k, p] for p in positions))
        return where, [{p: at[k, p] for p in positions} for k in range(n)]

    island, (Pwana, Quero, Rayou, Skern) = placed(["Pwana", "Quero", "Rayou", "Skern"])
    export, (alabaster, bananas, coconuts, durian_fruit) = placed(
        ["alabaster", "bananas", "coconuts", "durian_fruit"])
    attraction, (resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve) = placed(
        ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"])

    def one_of(cases, name):
        # At least one case holds; a case (x at p and y at q) is a binary that can be 1 only
        # when both placements hold.
        chosen = []
        for c, (x, p, y, q) in enumerate(cases):
            both = model.binary_var(name=f"{name}_{c}")
            model.add_constraint(both <= x[p])
            model.add_constraint(both <= y[q])
            chosen.append(both)
        model.add_constraint(model.sum(chosen) >= 1)

    # 1. The island with the koala preserve is due south of Pwana.
    one_of([(Pwana, A, koala_preserve, C), (Pwana, B, koala_preserve, D)], "clue1")
    # 2. The island with the alabaster quarry is due west of Quero.
    one_of([(alabaster, A, Quero, B), (alabaster, C, Quero, D)], "clue2")
    # 3. The island with the resort hotel is due east of the one exporting durian fruit.
    one_of([(durian_fruit, A, resort_hotel, B), (durian_fruit, C, resort_hotel, D)], "clue3")
    # 4. Skern and the island with the jai alai stadium share a north-south bridge.
    one_of([(Skern, A, jai_alai_stadium, C), (Skern, C, jai_alai_stadium, A),
            (Skern, B, jai_alai_stadium, D), (Skern, D, jai_alai_stadium, B)], "clue4")
    # 5. Rayou and the island exporting bananas share an east-west bridge.
    one_of([(Rayou, A, bananas, B), (Rayou, B, bananas, A),
            (Rayou, C, bananas, D), (Rayou, D, bananas, C)], "clue5")
    # 6. The ice skating rink and the jai alai stadium are not joined by a bridge: they sit
    # on opposite corners of the square.
    one_of([(ice_skating_rink, A, jai_alai_stadium, D), (ice_skating_rink, D, jai_alai_stadium, A),
            (ice_skating_rink, B, jai_alai_stadium, C), (ice_skating_rink, C, jai_alai_stadium, B)],
           "clue6")

    return model, {"island": island, "export": export, "attraction": attraction}
