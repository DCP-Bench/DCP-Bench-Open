# Wolf, goat and cabbage river crossing: a farmer ferries a wolf, a goat and a cabbage
# across a river. Each state records, per item, whether it is on the destination shore (1)
# or the starting shore (0), plus the boat. Stages run 0..stage-1; stage 0 has everything
# on the starting shore and the last stage has everything on the destination shore.
import cvc5.pythonic as cz


def build(instance):
    n = instance["stage"]

    boat = [cz.Bool(f"boat_{i}") for i in range(n)]
    wolf = [cz.Bool(f"wolf_{i}") for i in range(n)]
    goat = [cz.Bool(f"goat_{i}") for i in range(n)]
    cabbage = [cz.Bool(f"cabbage_{i}") for i in range(n)]

    constraints = []

    # The description starts everything on the starting shore (0) and ends with everything
    # on the destination shore (1).
    constraints += [cz.Not(boat[0]), cz.Not(wolf[0]), cz.Not(goat[0]), cz.Not(cabbage[0])]
    constraints += [boat[n - 1], wolf[n - 1], goat[n - 1], cabbage[n - 1]]

    # The boat can carry only the farmer and a single item, so each stage it crosses the river
    # and takes at most one item along. The boat alternates shores at every stage.
    # An item changes shore only when it travels with the boat.
    # At most one item moves between two consecutive stages.
    for i in range(n - 1):
        constraints.append(boat[i] != boat[i + 1])
        w_moves = cz.Xor(wolf[i], wolf[i + 1])
        g_moves = cz.Xor(goat[i], goat[i + 1])
        c_moves = cz.Xor(cabbage[i], cabbage[i + 1])
        constraints.append(cz.Implies(w_moves, wolf[i] == boat[i]))
        constraints.append(cz.Implies(g_moves, goat[i] == boat[i]))
        constraints.append(cz.Implies(c_moves, cabbage[i] == boat[i]))
        constraints.append(cz.Not(cz.And(w_moves, g_moves)))
        constraints.append(cz.Not(cz.And(w_moves, c_moves)))
        constraints.append(cz.Not(cz.And(g_moves, c_moves)))

    # If left unattended together, the wolf would eat the goat, or the goat would eat the
    # cabbage. Every stage: the farmer must be on the shore with the goat when the wolf
    # and the goat share a shore, and with the cabbage when the goat and cabbage share one.
    for i in range(n):
        constraints.append(cz.Implies(wolf[i] == goat[i], boat[i] == goat[i]))
        constraints.append(cz.Implies(goat[i] == cabbage[i], boat[i] == goat[i]))

    outputs = {
        "boat_pos": boat,
        "wolf_pos": wolf,
        "goat_pos": goat,
        "cabbage_pos": cabbage,
    }
    return constraints, outputs
