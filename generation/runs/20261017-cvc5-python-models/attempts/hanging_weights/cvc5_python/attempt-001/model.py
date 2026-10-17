# hanging_weights: weights A-M hang from a system of bars. Each weight is an
# integer in 1..13. Find the weights (a..m) so the diagram balances: at every
# pivot the weights on either side are equal when weighted by distance from the
# pivot, and a bar hanging beneath another contributes its total weight as a
# single weight.
#
# Bar structure read from the diagram (arm lengths in units of one segment):
#   top bar:   pivot between the LM bar (arm 4) and the JK bar (arm 3)
#   LM bar:    H-bar subtree (arm 1), L (arm 1), M (arm 4), pivot at the top-bar string
#   H bar:     H (arm 3), EF bar (arm 2), I (arm 3), pivot at the LM bar's left end
#   EF bar:    E (arm 3), F (arm 2)
#   JK bar:    AB bar (arm 3), J (arm 2), K (arm 1), G bar (arm 2), pivot at the top-bar string
#   AB bar:    A (arm 4), B (arm 1)
#   G bar:     G (arm 3), CD bar (arm 2)
#   CD bar:    C (arm 5), D (arm 1)

import cvc5.pythonic as cz


def build(instance):
    a, b, c, d, e, f, g, h, i, j, k, l, m = cz.Ints("a b c d e f g h i j k l m")
    weights = [a, b, c, d, e, f, g, h, i, j, k, l, m]

    # Each weight has an integer value between 1 and 13.
    domain = [w >= 1 for w in weights] + [w <= 13 for w in weights]

    # Subtree totals: a bar hanging beneath another counts as its total weight.
    h_sub = h + i + e + f          # H bar with I and the EF bar
    lm_total = h_sub + l + m       # LM bar with its hanging parts
    jk_total = a + b + j + k + g + c + d  # JK bar with its hanging parts

    constraints = list(domain)

    # The top bar: the weights on either side of its pivot must balance.
    constraints.append(4 * lm_total == 3 * jk_total)

    # The bar LM: the H bar (distance 1) balances L (distance 1) and M (distance 4).
    constraints.append(h_sub == l + 4 * m)

    # The bar H: the weights on either side of its pivot must balance.
    # Read from the diagram: H at distance 3, the EF bar at distance 2, I at distance 3.
    constraints.append(3 * h == 2 * (e + f) + 3 * i)

    # The bar EF: 3*E=2*F.
    constraints.append(3 * e == 2 * f)

    # The bar JK: the weights on either side of its pivot must balance.
    # The AB bar at distance 3, J at distance 2, K at distance 1, the G bar at distance 2.
    constraints.append(3 * (a + b) + 2 * j == k + 2 * (g + c + d))

    # The bar AB: 4*A=B.
    constraints.append(4 * a == b)

    # The bar G, the one above the bottom right bar: 3*G=2*(C+D).
    constraints.append(3 * g == 2 * (c + d))

    # The bottom right bar: 5*C=D.
    constraints.append(5 * c == d)

    outputs = {
        "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
        "h": h, "i": i, "j": j, "k": k, "l": l, "m": m,
    }
    return constraints, outputs
