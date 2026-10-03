"""Initials queue: ten people queue with initials that are alphabetically ordered pairs of
distinct letters from A..E, no two alike and no one sharing a letter with the person in front.
BE is first, CD second and BD last. Find the queue.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Letters A..E are 0..4; the queue length and the known
    # places are from the statement.
    n = 10
    A, B, C, D, E = range(5)
    letters = range(5)
    # Every alphabetically ordered pair of distinct letters a < b.
    pairs = [(a, b) for a in letters for b in letters if a < b]
    places = range(n)

    model = Model("initials_queue")

    # has[i, p] is 1 when person i has initials pairs[p]; each person has one pair.
    has = {(i, p): model.binary_var(name=f"person_{i}_pair_{p}") for i in places
           for p in range(len(pairs))}
    for i in places:
        model.add_constraint(model.sum(has[i, p] for p in range(len(pairs))) == 1)

    # No two people have the same initials.
    for p in range(len(pairs)):
        model.add_constraint(model.sum(has[i, p] for i in places) <= 1)

    def uses(i, letter):
        # 1 when person i's initials contain the letter.
        return model.sum(has[i, p] for p, pair in enumerate(pairs) if letter in pair)

    # No one shares a letter with the person in front.
    for i in range(n - 1):
        for letter in letters:
            model.add_constraint(uses(i, letter) + uses(i + 1, letter) <= 1)

    # BE is at the front, CD right behind, and BD at the end.
    model.add_constraint(has[0, pairs.index((B, E))] == 1)
    model.add_constraint(has[1, pairs.index((C, D))] == 1)
    model.add_constraint(has[n - 1, pairs.index((B, D))] == 1)

    # queue[i] is the pair of initials of person i, read from the chosen pair.
    queue = [[model.sum(pair[s] * has[i, p] for p, pair in enumerate(pairs) if pair[s])
              for s in range(2)] for i in places]

    return model, {"queue": queue}
