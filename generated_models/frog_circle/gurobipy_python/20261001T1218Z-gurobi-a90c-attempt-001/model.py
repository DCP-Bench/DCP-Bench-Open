"""Frog circle: arrange cards 1..n on a circle so that a frog starting on card 1 and jumping k places clockwise from card k lands on every card."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    places = range(n)
    cards = range(1, n + 1)

    model = gp.Model("frog_circle")

    # card_at[p, k] is 1 when place p holds card k. The cards are all different,
    # so they form a permutation of 1..n over the places.
    card_at = model.addVars(places, cards, vtype=GRB.BINARY, name="card_at")
    for p in places:
        model.addConstr(card_at.sum(p, "*") == 1, name=f"place[{p}]")
    for k in cards:
        model.addConstr(card_at.sum("*", k) == 1, name=f"card[{k}]")
    x = [gp.quicksum(k * card_at[p, k] for k in cards) for p in places]

    # The frog starts on card 1 at place 0.
    model.addConstr(card_at[0, 1] == 1, name="start_card")

    # From place p the frog jumps x[p] places clockwise, to (p + x[p]) mod n.
    # A jump from p to another place q therefore needs card (q - p) mod n at p.
    # jump[p, q] is 1 when the frog makes that jump within its first n - 1 jumps.
    jump = model.addVars([(p, q) for p in places for q in places if p != q], vtype=GRB.BINARY, name="jump")
    for (p, q) in jump:
        model.addConstr(jump[p, q] <= card_at[p, (q - p) % n], name=f"jump_card[{p},{q}]")

    # The frog lands on every place: its first n places are all different. The
    # n - 1 jumps then form one path from place 0 through every place: at most
    # one jump leaves and at most one arrives at each place, none arrives at
    # the start, and there are n - 1 of them.
    for p in places:
        model.addConstr(gp.quicksum(jump[p, q] for q in places if q != p) <= 1, name=f"leave[{p}]")
        model.addConstr(gp.quicksum(jump[q, p] for q in places if q != p) <= 1, name=f"arrive[{p}]")
    model.addConstr(gp.quicksum(jump[q, 0] for q in places if q != 0) == 0, name="no_return_to_start")
    model.addConstr(jump.sum() == n - 1, name="jump_count")

    # step[p] is the jump number at which the frog reaches place p (place 0 at
    # step 0); every jump reaches the next step, which rules out closed loops.
    step = model.addVars(places, lb=0, ub=n - 1, vtype=GRB.INTEGER, name="step")
    model.addConstr(step[0] == 0, name="start_place")
    for (p, q) in jump:
        model.addConstr((jump[p, q] == 1) >> (step[q] == step[p] + 1), name=f"order[{p},{q}]")

    return model, {"x": x}
