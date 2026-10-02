# Four islands: four islands joined by bridges (A and B on the north, C and D on the south,
# A-B, C-D, A-C and B-D bridged) each have a name, a main export and a tourist attraction, all
# different. Use six clues about their relative positions to say which map position holds each
# island name, each export and each attraction.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 4
    A, B, C, D = range(n)  # map positions: A is north-west, B north-east, C south-west, D south-east

    def row(p):
        return p // 2  # 0 for the northern islands, 1 for the southern ones

    def column(p):
        return p % 2   # 0 for the western islands, 1 for the eastern ones

    def due_south(p, q):
        """Island q is due south of island p."""
        return column(p) == column(q) and row(q) == row(p) + 1

    def due_west(p, q):
        """Island p is due west of island q."""
        return row(p) == row(q) and column(p) + 1 == column(q)

    def north_south_bridge(p, q):
        return column(p) == column(q) and row(p) != row(q)

    def east_west_bridge(p, q):
        return row(p) == row(q) and column(p) != column(q)

    def connected(p, q):
        return north_south_bridge(p, q) or east_west_bridge(p, q)

    pool = IDPool()

    def positions(name):
        return [Integer(f"{name}{i}", 0, n - 1, vpool=pool) for i in range(n)]

    # island[i] = the map position of the i-th island (Pwana, Quero, Rayou, Skern)
    island = positions("island")
    Pwana, Quero, Rayou, Skern = island
    # export[i] = the map position of the island exporting alabaster, bananas, coconuts, durian fruit
    export = positions("export")
    alabaster, bananas, coconuts, durian_fruit = export
    # attraction[i] = the map position of the island with the resort hotel, the ice skating
    # rink, the jai alai stadium, the koala preserve
    attraction = positions("attraction")
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    engine = IntegerEngine(vars=island + export + attraction, vpool=pool)

    # every name, every export and every attraction belongs to a different island
    engine.add_alldifferent(island)
    engine.add_alldifferent(export)
    engine.add_alldifferent(attraction)

    cnf = engine.clausify()

    def require(x, y, holds):
        """The pair of map positions (x, y) has to satisfy holds(x, y): every other pair of
        values is ruled out."""
        for p in range(n):
            for q in range(n):
                if not holds(p, q):
                    cnf.append([-x.equals(p), -y.equals(q)])

    # 1. The island with the koala preserve is due south of Pwana.
    require(Pwana, koala_preserve, due_south)
    # 2. The island with the largest alabaster quarry is due west of Quero.
    require(alabaster, Quero, due_west)
    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    require(durian_fruit, resort_hotel, due_west)
    # 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
    require(Skern, jai_alai_stadium, north_south_bridge)
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    require(Rayou, bananas, east_west_bridge)
    # 6. The islands with the ice skating rink and the jai alai stadium are not connected by a
    #    bridge (they are not the same island either, as the attractions differ).
    require(ice_skating_rink, jai_alai_stadium, lambda p, q: p != q and not connected(p, q))

    return cnf, {"island": island, "export": export, "attraction": attraction}
