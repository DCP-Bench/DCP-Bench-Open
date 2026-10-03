"""Frog circle: the cards 1..n are arranged on a circle of n places; a frog starts on card 1
at place 0 and, from a card k, jumps k places clockwise, forever. Find an arrangement of
the cards in which the frog lands on every card.

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

    # From place p the frog jumps to place (p + x[p]) mod n. jump[p][q] = 1 if it goes from p
    # to q, which is the card k with k = (q - p) mod n (card n when q = p, a jump around the
    # whole circle).
    def jump_card(p, q):
        return (q - p) % n or n

    # The frog lands on every place exactly once: every place is reached from exactly one
    # place, and the jumps form a single cycle through place 0 of all n places.
    for q in range(n):
        problem += pulp.lpSum(put[p][jump_card(p, q)] for p in range(n)) == 1

    # Single cycle (no separate loops among the other places): visit[p] is the step at which
    # the frog is on place p (place 0 is step 0). A jump from p to q != 0 goes to a later
    # step, which is impossible around a closed loop that does not contain place 0.
    visit = [pulp.LpVariable(f"visit_{p}", 0, n - 1, cat="Integer") for p in range(n)]
    problem += visit[0] == 0
    for p in range(n):
        for q in range(1, n):
            problem += visit[q] >= visit[p] + 1 - n * (1 - put[p][jump_card(p, q)])

    return problem, {"x": x}
