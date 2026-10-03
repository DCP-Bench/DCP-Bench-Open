"""Four islands: find the name, export and tourist attraction of each of four islands joined by bridges."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. Map positions: A=0 (north-west),
# B=1 (north-east), C=2 (south-west), D=3 (south-east); bridges join A-B, C-D
# (east-west) and A-C, B-D (north-south).
A, B, C, D = range(4)
POSITIONS = range(4)
ISLANDS = ["Pwana", "Quero", "Rayou", "Skern"]
EXPORTS = ["alabaster", "bananas", "coconuts", "durian_fruit"]
ATTRACTIONS = ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"]


def build(instance):
    model = gp.Model("four_islands")

    # at[name, p] = 1 when that island, export or attraction is at position p.
    # Within each group the four items occupy the four positions, one each.
    at = {}
    for group in (ISLANDS, EXPORTS, ATTRACTIONS):
        for item in group:
            for p in POSITIONS:
                at[item, p] = model.addVar(vtype=GRB.BINARY, name=f"at[{item},{p}]")
            model.addConstr(gp.quicksum(at[item, p] for p in POSITIONS) == 1, name=f"placed[{item}]")
        for p in POSITIONS:
            model.addConstr(gp.quicksum(at[item, p] for item in group) == 1, name=f"different[{group[0]},{p}]")

    def one_of(name, pairs):
        """At least one of the listed (item1 at p1 and item2 at p2) holds: each
        option is a binary that can be 1 only if both placements hold."""
        options = []
        for k, ((x, px), (y, py)) in enumerate(pairs):
            w = model.addVar(vtype=GRB.BINARY, name=f"{name}[{k}]")
            model.addConstr(w <= at[x, px])
            model.addConstr(w <= at[y, py])
            options.append(w)
        model.addConstr(gp.quicksum(options) >= 1, name=name)

    # 1. The island with the koala preserve is due south of Pwana.
    one_of("clue1", [(("Pwana", A), ("koala_preserve", C)), (("Pwana", B), ("koala_preserve", D))])

    # 2. The island with the alabaster quarry is due west of Quero.
    one_of("clue2", [(("alabaster", A), ("Quero", B)), (("alabaster", C), ("Quero", D))])

    # 3. The island with the resort hotel is due east of the one exporting durian fruit.
    one_of("clue3", [(("durian_fruit", A), ("resort_hotel", B)), (("durian_fruit", C), ("resort_hotel", D))])

    # 4. Skern and the island with the jai alai stadium share a north-south bridge.
    one_of("clue4", [(("Skern", A), ("jai_alai_stadium", C)), (("Skern", C), ("jai_alai_stadium", A)),
                     (("Skern", B), ("jai_alai_stadium", D)), (("Skern", D), ("jai_alai_stadium", B))])

    # 5. Rayou and the island exporting bananas share an east-west bridge.
    one_of("clue5", [(("Rayou", A), ("bananas", B)), (("Rayou", B), ("bananas", A)),
                     (("Rayou", C), ("bananas", D)), (("Rayou", D), ("bananas", C))])

    # 6. The ice skating rink and the jai alai stadium are not joined by a
    #    bridge, so they sit on opposite corners.
    one_of("clue6", [(("ice_skating_rink", A), ("jai_alai_stadium", D)),
                     (("ice_skating_rink", D), ("jai_alai_stadium", A)),
                     (("ice_skating_rink", B), ("jai_alai_stadium", C)),
                     (("ice_skating_rink", C), ("jai_alai_stadium", B))])

    def position(item):
        return gp.quicksum(p * at[item, p] for p in POSITIONS)

    return model, {
        "island": [position(i) for i in ISLANDS],
        "export": [position(e) for e in EXPORTS],
        "attraction": [position(a) for a in ATTRACTIONS],
    }
