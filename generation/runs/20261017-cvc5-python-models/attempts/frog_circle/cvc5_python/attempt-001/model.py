# frog_circle: cards numbered 1 to n are arranged in a circle. The frog starts on
# card 1 and jumps 1 place clockwise, then from card k jumps k places clockwise,
# forever. Find an arrangement in which the frog lands on every card.
# x[p] is the card at position p (0-based, clockwise); card 1 is at position 0.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    x = [cz.Int(f"x{p}") for p in range(n)]
    # t[p] is the step at which the frog lands on position p; the frog starts at 0.
    t = [cz.Int(f"t{p}") for p in range(n)]

    cons = []

    # Card numbers, one per position: the arrangement is a permutation of 1..n.
    # Card 1 is at the first position of the list.
    # cvc5 integers are unbounded, so the bounds must be added.
    for p in range(n):
        cons.append(x[p] >= 1)
        cons.append(x[p] <= n)
    cons.append(cz.Distinct(x))
    cons.append(x[0] == 1)

    # The frog visits every card: its landing steps are a permutation of 0..n-1,
    # and the frog starts on position 0 at step 0.
    for p in range(n):
        cons.append(t[p] >= 0)
        cons.append(t[p] <= n - 1)
    cons.append(cz.Distinct(t))
    cons.append(t[0] == 0)

    # From the card at position p (card value x[p]), the frog jumps x[p] places
    # clockwise, landing on position (p + x[p]) mod n.
    # Each landing is the next step: while the frog has not made its last step,
    # the position it jumps to is the one visited at the next step.
    for p in range(n):
        landing = cz.If(p + x[p] >= n, p + x[p] - n, p + x[p])
        for q in range(n):
            cons.append(
                cz.Implies(
                    cz.And(t[p] < n - 1, landing == q),
                    t[q] == t[p] + 1,
                )
            )

    return cons, {"x": x}
