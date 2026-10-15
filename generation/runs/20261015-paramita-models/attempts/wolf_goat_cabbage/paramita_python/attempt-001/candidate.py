# Wolf, goat and cabbage river crossing. A farmer rows a boat across a river
# with a wolf, a goat and a cabbage. Each stage is a state of the crossing:
# which shore each item and the boat are on (1 = destination shore, 0 = starting
# shore). The number of stages comes from the instance; stage 0 is the start,
# the last stage is the finish.
from paramita.modelling import Bool, If, Iff

ITEMS = ["wolf", "goat", "cabbage"]


def build(instance):
    n = instance["stage"]
    pos = {it: [Bool(f"{it}_pos_{t}") for t in range(n)] for it in ITEMS}
    boat = [Bool(f"boat_pos_{t}") for t in range(n)]
    cons = []

    # the farmer, the wolf, the goat, the cabbage and the boat all start on the starting shore
    cons += [~pos[it][0] for it in ITEMS]
    cons += [~boat[0]]

    # all of them reach the destination shore at the last stage
    cons += [pos[it][n - 1] for it in ITEMS]
    cons += [boat[n - 1]]

    # the farmer rows the boat across at every stage, so the boat alternates shores
    for t in range(n - 1):
        cons.append(Iff(boat[t], ~boat[t + 1]))

    # the boat can carry only the farmer and a single item:
    # an item crosses when it changes shore, at most one item per crossing,
    # and it crosses only from the shore the farmer is on
    for t in range(n - 1):
        moves = []
        for it in ITEMS:
            m = Bool(f"{it}_crosses_{t}")
            cons.append(Iff(m, pos[it][t] + pos[it][t + 1] == 1))
            cons.append(If(m, Iff(pos[it][t], boat[t])))
            moves.append(m)
        cons.append(sum(moves) <= 1)

    # if left unattended together, the wolf would eat the goat:
    # wherever the wolf and the goat are, the farmer is with the goat
    for t in range(n):
        cons.append(If(Iff(pos["wolf"][t], pos["goat"][t]),
                       Iff(boat[t], pos["goat"][t])))

    # if left unattended together, the goat would eat the cabbage:
    # wherever the goat and the cabbage are, the farmer is with the goat
    for t in range(n):
        cons.append(If(Iff(pos["goat"][t], pos["cabbage"][t]),
                       Iff(boat[t], pos["goat"][t])))

    outputs = {
        "wolf_pos": pos["wolf"],
        "goat_pos": pos["goat"],
        "cabbage_pos": pos["cabbage"],
        "boat_pos": boat,
    }
    return cons, outputs
