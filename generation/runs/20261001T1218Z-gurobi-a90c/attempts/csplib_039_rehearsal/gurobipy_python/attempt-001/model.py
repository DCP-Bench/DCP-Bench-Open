"""Rehearsal problem: order the pieces so that the total time players spend present but not playing is minimal."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]  # duration[p] of piece p
    plays = instance["rehearsal"]  # plays[pl][p] is 1 when player pl plays in piece p
    slots = range(n)
    pieces = range(n)
    players = range(num_players)

    model = gp.Model("rehearsal")

    # at[i, p] is 1 when piece p is rehearsed in slot i: each slot holds one
    # piece and each piece is rehearsed once, so the order is a permutation.
    at = model.addVars(slots, pieces, vtype=GRB.BINARY, name="at")
    for i in slots:
        model.addConstr(at.sum(i, "*") == 1, name=f"slot[{i}]")
    for p in pieces:
        model.addConstr(at.sum("*", p) == 1, name=f"piece[{p}]")

    # A player is present from arrival to departure. arrived[pl, i] is 1 from the
    # arrival slot on and never drops back; staying[pl, i] is 1 up to the
    # departure slot and never rises again. The player is present in slot i
    # when both hold, which makes presence one contiguous block of slots.
    arrived = model.addVars(players, slots, vtype=GRB.BINARY, name="arrived")
    staying = model.addVars(players, slots, vtype=GRB.BINARY, name="staying")
    present = {}
    for pl in players:
        for i in slots:
            if i + 1 < n:
                model.addConstr(arrived[pl, i] <= arrived[pl, i + 1], name=f"arrive_once[{pl},{i}]")
                model.addConstr(staying[pl, i] >= staying[pl, i + 1], name=f"depart_once[{pl},{i}]")
            model.addConstr(arrived[pl, i] + staying[pl, i] >= 1, name=f"arrive_before_depart[{pl},{i}]")
            present[pl, i] = arrived[pl, i] + staying[pl, i] - 1

            # A player must be present for every piece they play.
            playing = gp.quicksum(at[i, p] for p in pieces if plays[pl][p])
            model.addConstr(playing <= present[pl, i], name=f"present_to_play[{pl},{i}]")

    # waiting[pl, i, p] is 1 when player pl is present in slot i, piece p is
    # rehearsed there and pl does not play in it. Since the objective is
    # minimised, a lower bound on the conjunction suffices.
    waiting = model.addVars(
        [(pl, i, p) for pl in players for i in slots for p in pieces if not plays[pl][p]],
        lb=0, ub=1, vtype=GRB.CONTINUOUS, name="waiting",
    )
    for (pl, i, p) in waiting:
        model.addConstr(waiting[pl, i, p] >= present[pl, i] + at[i, p] - 1, name=f"wait[{pl},{i},{p}]")

    # Total waiting time: the duration of every piece a present player sits out.
    model.setObjective(gp.quicksum(duration[p] * waiting[pl, i, p] for (pl, i, p) in waiting), GRB.MINIMIZE)

    rehearsal_order = [gp.quicksum(p * at[i, p] for p in pieces) for i in slots]
    return model, {"rehearsal_order": rehearsal_order}
