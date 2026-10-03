"""Frog circle: the cards 1..n are arranged on a circle of n places; a frog starts on card 1
at place 0 and, from a card k, jumps k places clockwise. Find an arrangement of the cards
in which the frog lands on every card: its first n places (the start and n - 1 jumps) are all
different.

The model reports the card at each place (place 0 holds card 1).
"""
import pulp


def build(instance):
    n = instance["n"]

    problem = pulp.LpProblem("frog_circle", pulp.LpMinimize)  # satisfaction: no objective

    # put[p][k] = 1 if place p holds card k (1..n). x[p] reads the card back. The cards
    # are all different, so the cards form a permutation of 1..n over the places.
    put = pulp.LpVariable.dicts("put", (range(n), range(1, n + 1)), cat="Binary")
    x = [pulp.LpVariable(f"x_{p}", 1, n, cat="Integer") for p in range(n)]
    for p in range(n):
        # each place holds one card
        problem += pulp.lpSum(put[p][k] for k in range(1, n + 1)) == 1
        problem += x[p] == pulp.lpSum(k * put[p][k] for k in range(1, n + 1))
    for k in range(1, n + 1):
        # each card is at one place
        problem += pulp.lpSum(put[p][k] for p in range(n)) == 1

    # the frog starts on card 1 at place 0
    problem += put[0][1] == 1

    # From place p the frog jumps to place (p + x[p]) mod n, so a jump from p to q is made by
    # the card k with k = (q - p) mod n (card n when q = p, a jump around the whole circle).
    def jump_card(p, q):
        return (q - p) % n or n

    # The frog's visits form a path through all n places that starts at place 0 and has
    # n - 1 jumps (the jump made from the last place is not constrained). step[p][q] = 1 if
    # the frog jumps from p to q along this path: it then uses the card at p that makes
    # exactly that jump.
    step = {(p, q): pulp.LpVariable(f"step_{p}_{q}", cat="Binary")
            for p in range(n) for q in range(n) if p != q}
    for (p, q), var in step.items():
        problem += var <= put[p][jump_card(p, q)]
    for p in range(n):
        # at most one jump leaves a place and at most one arrives in it
        problem += pulp.lpSum(step[(p, q)] for q in range(n) if q != p) <= 1
        problem += pulp.lpSum(step[(q, p)] for q in range(n) if q != p) <= 1
    # no jump arrives at the starting place, and the n - 1 jumps join all n places
    problem += pulp.lpSum(step[(q, 0)] for q in range(1, n)) == 0
    problem += pulp.lpSum(step.values()) == n - 1

    # No jumps in a closed loop: visit[p] is the step at which the frog is on place p
    # (place 0 is step 0); every jump of the path goes to a later step. Together with the
    # degree limits above, the jumps then form one path covering every place.
    visit = [pulp.LpVariable(f"visit_{p}", 0, n - 1, cat="Integer") for p in range(n)]
    problem += visit[0] == 0
    for (p, q), var in step.items():
        problem += visit[q] >= visit[p] + 1 - n * (1 - var)

    return problem, {"x": x}
