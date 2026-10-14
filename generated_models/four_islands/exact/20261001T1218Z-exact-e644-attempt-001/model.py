# Four islands: four islands (Pwana, Quero, Rayou, Skern) sit at the corners of a square map
# A B / C D, joined by bridges. Each has a different export and a different tourist attraction.
# Place every island, export and attraction on a map position (A=0, B=1, C=2, D=3) using the clues.
from exact import Exact


def build(instance):
    # This problem has no instance data. The map and the four items of each kind belong to the
    # problem statement.
    n = 4
    A, B, C, D = range(n)  # map positions: A is north-west, B north-east, C south-west, D south-east
    kinds = {
        "island": ["Pwana", "Quero", "Rayou", "Skern"],
        "export": ["alabaster", "bananas", "coconuts", "durian_fruit"],
        "attraction": ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"],
    }

    solver = Exact()

    # Each item takes a map position; is_at[item][pos] = 1 when it is placed at that position.
    is_at = {}
    for items in kinds.values():
        for item in items:
            solver.addVariable(item, 0, n - 1)
            is_at[item] = [f"{item}_at_{pos}" for pos in range(n)]
            for indicator in is_at[item]:
                solver.addVariable(indicator, 0, 1)
            solver.addConstraint([(1, indicator) for indicator in is_at[item]], True, 1, True, 1)
            solver.addConstraint([(pos, is_at[item][pos]) for pos in range(1, n)] +
                                 [(-1, item)], True, 0, True, 0)
        # All items of one kind sit at different positions.
        for pos in range(n):
            solver.addConstraint([(1, is_at[item][pos]) for item in items], True, 1, True, 1)

    def one_of(label, options):
        # At least one of the listed placements holds. Each option is a list of (item, position)
        # pairs that must all be true together; a 0/1 variable per option says it is the one
        # chosen, and choosing it forces every placement it lists.
        chosen = []
        for k, option in enumerate(options):
            pick = f"{label}_option_{k}"
            solver.addVariable(pick, 0, 1)
            chosen.append((1, pick))
            for item, pos in option:
                solver.addConstraint([(1, is_at[item][pos]), (-1, pick)], True, 0)
        solver.addConstraint(chosen, True, 1)

    pwana, quero, rayou, skern = kinds["island"]
    alabaster, bananas, coconuts, durian_fruit = kinds["export"]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = kinds["attraction"]

    # 1. The island noted for its koala preserve is due south of Pwana.
    one_of("clue1", [[(pwana, A), (koala_preserve, C)],
                     [(pwana, B), (koala_preserve, D)]])
    # 2. The island with the largest alabaster quarry is due west of Quero.
    one_of("clue2", [[(alabaster, A), (quero, B)],
                     [(alabaster, C), (quero, D)]])
    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    one_of("clue3", [[(durian_fruit, A), (resort_hotel, B)],
                     [(durian_fruit, C), (resort_hotel, D)]])
    # 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
    one_of("clue4", [[(skern, A), (jai_alai_stadium, C)],
                     [(skern, C), (jai_alai_stadium, A)],
                     [(skern, B), (jai_alai_stadium, D)],
                     [(skern, D), (jai_alai_stadium, B)]])
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    one_of("clue5", [[(rayou, A), (bananas, B)],
                     [(rayou, B), (bananas, A)],
                     [(rayou, C), (bananas, D)],
                     [(rayou, D), (bananas, C)]])
    # 6. The islands with the ice skating rink and with the jai alai stadium are not connected by a
    #    bridge: they sit at opposite corners (A and D, or B and C).
    one_of("clue6", [[(ice_skating_rink, A), (jai_alai_stadium, D)],
                     [(ice_skating_rink, D), (jai_alai_stadium, A)],
                     [(ice_skating_rink, B), (jai_alai_stadium, C)],
                     [(ice_skating_rink, C), (jai_alai_stadium, B)]])

    return solver, {kind: items for kind, items in kinds.items()}
