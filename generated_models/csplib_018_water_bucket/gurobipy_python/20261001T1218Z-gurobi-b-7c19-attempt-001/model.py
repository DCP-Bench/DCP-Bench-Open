"""Water bucket (CSPLib 18): pour water between three buckets to reach a goal state in the fewest transfers."""
import itertools

import gurobipy as gp
from gurobipy import GRB


def build(instance):
    capacities = instance["capacities"]
    initial_state = tuple(instance["initial_state"])
    goal_state = tuple(instance["goal_state"])
    steps = instance["MAX_STEPS"]
    pad = instance["PADDING_VALUE"]
    buckets = range(len(capacities))

    # As in the reference, the total amount of water is the largest initial
    # amount, and every unpadded state holds exactly that much, each bucket
    # within its capacity.
    total_water = max(initial_state)
    states = [s for s in itertools.product(*(range(c + 1) for c in capacities))
              if sum(s) == total_water]

    # A transfer pours from bucket i into bucket j until i is empty or j is
    # full, and must move some water. The reference's transition table lists
    # only states holding capacities[0] in total, so transfers exist only there.
    def successors(state):
        result = set()
        if sum(state) != capacities[0]:
            return result
        for i in buckets:
            for j in buckets:
                if i == j:
                    continue
                amount = min(state[i], capacities[j] - state[j])
                if amount > 0:
                    nxt = list(state)
                    nxt[i] -= amount
                    nxt[j] += amount
                    result.add(tuple(nxt))
        return result

    predecessors = {s: [] for s in states}
    for s in states:
        for nxt in successors(s):
            if nxt in predecessors:
                predecessors[nxt].append(s)

    model = gp.Model("water_bucket")

    # at[t, k] = 1 when step t is in state k; the last index is the padding state.
    padding = len(states)
    options = range(len(states) + 1)
    at = model.addVars(steps, options, vtype=GRB.BINARY, name="at")
    index = {s: k for k, s in enumerate(states)}
    goal = index.get(goal_state)

    # Every step is in exactly one state, real or padding.
    for t in range(steps):
        model.addConstr(at.sum(t, "*") == 1, name=f"one_state[{t}]")

    # The sequence starts with the initial state.
    if initial_state in index:
        model.addConstr(at[0, index[initial_state]] == 1, name="start")
    else:
        model.addConstr(at.sum(0, "*") == 0, name="start_impossible")

    for t in range(steps - 1):
        at_goal = at[t, goal] if goal is not None else 0
        # Once the goal is reached, and once padding has begun, every later
        # step is padding.
        model.addConstr(at[t + 1, padding] >= at[t, padding], name=f"stay_padded[{t}]")
        if goal is not None:
            model.addConstr(at[t + 1, padding] >= at_goal, name=f"pad_after_goal[{t}]")
        model.addConstr(at[t + 1, padding] <= at[t, padding] + at_goal, name=f"pad_only_after_goal[{t}]")
        # Otherwise the next state follows from the current one by a single
        # transfer: a state can be entered only from one of its predecessors,
        # and never from the goal.
        for s in states:
            sources = [index[p] for p in predecessors[s] if p != goal_state]
            model.addConstr(at[t + 1, index[s]] <= gp.quicksum(at[t, k] for k in sources),
                            name=f"transfer[{t},{index[s]}]")

    # The goal must be reached at some step.
    if goal is not None:
        model.addConstr(gp.quicksum(at[t, goal] for t in range(steps)) >= 1, name="reach_goal")
    else:
        model.addConstr(at.sum(0, "*") == 0, name="goal_impossible")

    # The amount in each bucket at each step, or the padding value.
    sequence = [[gp.quicksum(states[k][b] * at[t, k] for k in range(len(states))) + pad * at[t, padding]
                 for b in buckets] for t in range(steps)]

    # The cost is the number of transfers: unpadded steps minus one.
    cost = gp.quicksum(1 - at[t, padding] for t in range(steps)) - 1
    model.setObjective(cost, GRB.MINIMIZE)

    return model, {"cost": cost, "sequence": sequence}
