# Four islands: four islands joined by bridges each have a different name, export
# and tourist attraction. Use six clues to say which map position holds which.
#
#   (A) -- (B)
#    |      |
#   (C) -- (D)
import z3


def build(instance):
    del instance  # the puzzle states its own islands and clues

    n = 4
    A, B, C, D = range(n)  # map positions

    # Island names, exports and attractions are each placed on a different map
    # position (A=0, B=1, C=2, D=3).
    island = z3.IntVector("island", n)
    pwana, quero, rayou, skern = island

    export = z3.IntVector("export", n)
    alabaster, bananas, coconuts, durian_fruit = export

    attraction = z3.IntVector("attraction", n)
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    solver = z3.Solver()
    for v in list(island) + list(export) + list(attraction):
        solver.add(v >= 0, v <= n - 1)

    # Different islands have different positions, exports and attractions.
    solver.add(z3.Distinct(island))
    solver.add(z3.Distinct(export))
    solver.add(z3.Distinct(attraction))

    def related(first, second, pairs):
        # first and second occupy a pair of positions listed in `pairs`.
        return z3.Or([z3.And(first == a, second == b) for a, b in pairs])

    # Position pairs read off the map: (north, south) pairs, (west, east) pairs,
    # and the pairs joined or not joined by a bridge.
    south_of = [(A, C), (B, D)]
    east_of = [(A, B), (C, D)]
    north_south_bridge = south_of + [(c, a) for a, c in south_of]
    east_west_bridge = east_of + [(b, a) for a, b in east_of]
    no_bridge = [(A, D), (D, A), (B, C), (C, B)]  # diagonal positions

    # 1. The island noted for its koala preserve is due south of Pwana.
    solver.add(related(pwana, koala_preserve, south_of))

    # 2. The island with the largest alabaster quarry is due west of Quero.
    solver.add(related(alabaster, quero, east_of))

    # 3. The island with the resort hotel is due east of the one that exports
    #    durian fruit.
    solver.add(related(durian_fruit, resort_hotel, east_of))

    # 4. Skern and the island with the jai alai stadium are connected by a
    #    north-south bridge.
    solver.add(related(skern, jai_alai_stadium, north_south_bridge))

    # 5. Rayou and the island that exports bananas are connected by an east-west
    #    bridge.
    solver.add(related(rayou, bananas, east_west_bridge))

    # 6. The islands with the ice skating rink and the jai alai stadium are not
    #    connected by a bridge.
    solver.add(related(ice_skating_rink, jai_alai_stadium, no_bridge))

    return solver, {"island": list(island), "export": list(export),
                    "attraction": list(attraction)}
