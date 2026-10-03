"""Four islands: four islands A, B (north) and C, D (south), with bridges A-B, C-D, A-C and
B-D. Find each island's name (Pwana, Quero, Rayou, Skern), export (alabaster, bananas,
coconuts, durian fruit) and tourist attraction (hotel, ice skating rink, jai alai stadium,
koala preserve) from the clues.

The model reports, for every name, export and attraction, its map position (A=0, B=1,
C=2, D=3).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    n = 4
    A, B, C, D = range(n)
    groups = {
        "island": ["Pwana", "Quero", "Rayou", "Skern"],
        "export": ["alabaster", "bananas", "coconuts", "durian_fruit"],
        "attraction": ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"],
    }

    problem = pulp.LpProblem("four_islands", pulp.LpMinimize)  # satisfaction

    # at[item][pos] = 1 if the name, export or attraction is on the island at map position
    # pos; within each group every item has a different island
    at = {item: [pulp.LpVariable(f"at_{item}_{pos}", cat="Binary") for pos in range(n)]
          for items in groups.values() for item in items}
    for items in groups.values():
        for item in items:
            problem += pulp.lpSum(at[item]) == 1
        for pos in range(n):
            problem += pulp.lpSum(at[item][pos] for item in items) == 1

    count = [0]

    def one_of(cases):
        """At least one case holds; a case is a list of (item, position) that all hold.
        Each case gets an indicator that can only be 1 when all its parts are."""
        chosen = []
        for case in cases:
            count[0] += 1
            var = pulp.LpVariable(f"case_{count[0]}", cat="Binary")
            for item, pos in case:
                problem.addConstraint(var <= at[item][pos])
            chosen.append(var)
        problem.addConstraint(pulp.lpSum(chosen) >= 1)

    # 1. The island noted for its koala preserve is due south of Pwana.
    one_of([[("Pwana", A), ("koala_preserve", C)], [("Pwana", B), ("koala_preserve", D)]])
    # 2. The island with the largest alabaster quarry is due west of Quero.
    one_of([[("alabaster", A), ("Quero", B)], [("alabaster", C), ("Quero", D)]])
    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    one_of([[("durian_fruit", A), ("resort_hotel", B)], [("durian_fruit", C), ("resort_hotel", D)]])
    # 4. Skern and the island with the jai alai stadium are connected by a north-south
    #    bridge.
    one_of([[("Skern", A), ("jai_alai_stadium", C)], [("Skern", C), ("jai_alai_stadium", A)],
            [("Skern", B), ("jai_alai_stadium", D)], [("Skern", D), ("jai_alai_stadium", B)]])
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    one_of([[("Rayou", A), ("bananas", B)], [("Rayou", B), ("bananas", A)],
            [("Rayou", C), ("bananas", D)], [("Rayou", D), ("bananas", C)]])
    # 6. The islands with the ice skating rink and with the jai alai stadium are not
    #    connected by a bridge: they are diagonally opposite.
    one_of([[("ice_skating_rink", A), ("jai_alai_stadium", D)],
            [("ice_skating_rink", D), ("jai_alai_stadium", A)],
            [("ice_skating_rink", B), ("jai_alai_stadium", C)],
            [("ice_skating_rink", C), ("jai_alai_stadium", B)]])

    position = {item: pulp.lpSum(pos * var for pos, var in enumerate(at[item])) for item in at}
    return problem, {key: [position[item] for item in items] for key, items in groups.items()}
