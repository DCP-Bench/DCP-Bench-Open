# Wolf, goat and cabbage river crossing. A farmer rows a boat that carries the farmer
# and at most one of a wolf, a goat or a cabbage. Stages 0..T-1 with T = instance["stage"].
# Each position is 0 for the starting shore and 1 for the destination shore. Stage 0
# has everything on the starting shore; the last stage has everything on the destination.
# Output per stage: wolf_pos, goat_pos, cabbage_pos, boat_pos.
#
# Formulation: a time-expanded flow over the enumerated states (wolf, goat, cabbage, boat).
# One binary per stage and state, one binary per stage transition and edge.
import mip
from itertools import product


def safe(state):
    # If left unattended together, the wolf would eat the goat, or the goat would eat
    # the cabbage. The farmer must be on the same shore as the goat whenever the wolf
    # or the cabbage shares a shore with the goat.
    w, g, c, b = state
    if w == g and b != g:
        return False
    if g == c and b != g:
        return False
    return True


def successors(state):
    # The farmer rows across at every stage, so the boat flips shore. He takes either
    # nobody or one item that is on the boat's shore; the item flips shore with him.
    b = state[3]
    result = []
    for mover in (None, 0, 1, 2):
        nxt = list(state)
        nxt[3] = 1 - b
        if mover is not None:
            if state[mover] != b:
                continue
            nxt[mover] = 1 - state[mover]
        nxt = tuple(nxt)
        if safe(nxt):
            result.append(nxt)
    return result


def build(instance):
    T = instance["stage"]
    model = mip.Model(solver_name="CBC")

    states = [s for s in product((0, 1), repeat=4) if safe(s)]
    start = (0, 0, 0, 0)
    goal = (1, 1, 1, 1)

    succ = {s: [s2 for s2 in successors(s) if s2 in states] for s in states}
    pred = {s: [] for s in states}
    for s in states:
        for s2 in succ[s]:
            pred[s2].append(s)

    def name(s):
        return "".join(str(v) for v in s)

    # One binary per stage and state: x[t, s] is 1 when the system is in state s at stage t.
    x = {}
    for t in range(T):
        for s in states:
            x[t, s] = model.add_var(f"x_{t}_{name(s)}", var_type=mip.BINARY)

    # One binary per stage transition and edge: y[t, s, s2] is 1 when the system moves
    # from state s at stage t to state s2 at stage t+1.
    y = {}
    for t in range(T - 1):
        for s in states:
            for s2 in succ[s]:
                y[t, s, s2] = model.add_var(f"y_{t}_{name(s)}_{name(s2)}", var_type=mip.BINARY)

    # Each stage is in exactly one state.
    for t in range(T):
        model.add_constr(mip.xsum(x[t, s] for s in states) == 1)

    # Starting state: everything on the starting shore.
    model.add_constr(x[0, start] == 1)

    # Destination state: everything on the destination shore.
    model.add_constr(x[T - 1, goal] == 1)

    # Flow conservation: a state at stage t leaves along exactly one edge, and a state
    # at stage t+1 is entered along exactly one edge.
    for t in range(T - 1):
        for s in states:
            model.add_constr(mip.xsum(y[t, s, s2] for s2 in succ[s]) == x[t, s])
        for s2 in states:
            model.add_constr(mip.xsum(y[t, s, s2] for s in pred[s2]) == x[t + 1, s2])

    # Output binaries, one per item and boat position at each stage, tied to the state.
    wolf = [model.add_var(f"wolf_{t}", var_type=mip.BINARY) for t in range(T)]
    goat = [model.add_var(f"goat_{t}", var_type=mip.BINARY) for t in range(T)]
    cabbage = [model.add_var(f"cabbage_{t}", var_type=mip.BINARY) for t in range(T)]
    boat = [model.add_var(f"boat_{t}", var_type=mip.BINARY) for t in range(T)]
    for t in range(T):
        model.add_constr(wolf[t] == mip.xsum(x[t, s] for s in states if s[0] == 1))
        model.add_constr(goat[t] == mip.xsum(x[t, s] for s in states if s[1] == 1))
        model.add_constr(cabbage[t] == mip.xsum(x[t, s] for s in states if s[2] == 1))
        model.add_constr(boat[t] == mip.xsum(x[t, s] for s in states if s[3] == 1))

    outputs = {
        "wolf_pos": wolf,
        "goat_pos": goat,
        "cabbage_pos": cabbage,
        "boat_pos": boat,
    }
    return model, outputs
