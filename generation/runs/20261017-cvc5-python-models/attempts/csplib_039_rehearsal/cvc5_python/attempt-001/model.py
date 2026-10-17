# csplib_039_rehearsal: order the pieces of a concert so that the total time
# players spend waiting (present but not currently playing) is minimised.
from cvc5.pythonic import Int, Distinct, If, Or, And, Not, Implies, Sum


def anyof(terms):
    # Or needs at least two arguments; a single term is its own disjunction.
    return terms[0] if len(terms) == 1 else Or(terms)


def build(instance):
    n = instance["num_pieces"]
    num_players = instance["num_players"]
    dur = instance["duration"]
    rehearsal = instance["rehearsal"]

    # rehearsal_order[k] is the piece rehearsed in slot k, a permutation of the pieces
    order = [Int(f"order_{k}") for k in range(n)]
    constraints = []
    for k in range(n):
        constraints += [order[k] >= 0, order[k] <= n - 1]
    constraints.append(Distinct(order))

    # d[k] is the duration of the piece rehearsed in slot k
    d = [Int(f"d_{k}") for k in range(n)]
    for k in range(n):
        for i in range(n):
            constraints.append(Implies(order[k] == i, d[k] == dur[i]))

    # a player takes part in a piece with rehearsal[p][piece] = 1; only players
    # who take part in some piece are present at all
    active = [p for p in range(num_players) if any(rehearsal[p][i] == 1 for i in range(n))]
    # plays[p][k]: player p takes part in the piece rehearsed in slot k
    plays = {}
    for p in active:
        plays[p] = [
            anyof([order[k] == i for i in range(n) if rehearsal[p][i] == 1])
            for k in range(n)
        ]

    # players arrive immediately before their first piece and leave immediately
    # after their last piece: a player is present in slot k when some piece up to
    # slot k and some piece from slot k on involves him
    waiting = []
    for p in active:
        for k in range(n):
            before = anyof([plays[p][j] for j in range(k + 1)])
            after = anyof([plays[p][j] for j in range(k, n)])
            # waiting time: present, not playing, so the slot's duration counts
            waiting.append(If(And(before, after, Not(plays[p][k])), d[k], 0))

    total = Sum(waiting)
    return constraints, {"rehearsal_order": order}, ("minimize", total)
