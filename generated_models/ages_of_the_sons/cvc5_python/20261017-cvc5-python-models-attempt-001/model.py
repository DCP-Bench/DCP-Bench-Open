# Ages of the three sons: an old man's sons have ages A1 >= A2 >= A3 (oldest first).
# Clues from the description, in order:
#   1. The product of their ages is 36. Candidate triples are the ordered positive
#      triples with that product.
#   2. The mathematician needs more information: the sum of the ages equals the number
#      of windows, and the sum alone does not determine the triple (another triple with
#      product 36 has the same sum).
#   3. The oldest son has blue eyes (the oldest is unique: A1 > A2).
#   4. The mathematician now knows: among triples that satisfy clues 1 to 3, only one
#      has the sum of the true ages.
import cvc5.pythonic as cz


def build(instance):
    A1, A2, A3 = cz.Ints("A1 A2 A3")

    # Candidate triples: positive integers, ordered oldest first, whose product is 36.
    # The bounds 1..36 follow from the product being 36 with all factors at least 1.
    cands = [
        (a, b, c)
        for a in range(1, 37)
        for b in range(1, a + 1)
        for c in range(1, b + 1)
        if a * b * c == 36
    ]

    constraints = [A3 >= 1, A1 >= A2, A2 >= A3]

    # The product of their ages is 36.
    constraints.append(cz.Or([cz.And(A1 == a, A2 == b, A3 == c) for a, b, c in cands]))

    # Clue 2: the sum of the ages is not determined by the sum alone, so another
    # candidate triple (different from the true one) has the same sum.
    constraints.append(
        cz.Or([
            cz.And(A1 + A2 + A3 == a + b + c, cz.Or(A1 != a, A2 != b, A3 != c))
            for a, b, c in cands
        ])
    )

    # Clue 3: the oldest son is identified, so the oldest age is unique.
    constraints.append(A1 > A2)

    # Clue 4: among the triples that satisfy clues 1 to 3 (product 36, oldest unique,
    # sum not determined by the sum alone), the sum of the true ages picks out one triple.
    def unique_max(t):
        return t[0] > t[1]

    def ambiguous_sum(t):
        s = sum(t)
        return sum(1 for u in cands if sum(u) == s) >= 2

    survivors = [t for t in cands if unique_max(t) and ambiguous_sum(t)]
    for a, b, c in survivors:
        constraints.append(
            cz.Implies(
                A1 + A2 + A3 == a + b + c,
                cz.And(A1 == a, A2 == b, A3 == c),
            )
        )

    return constraints, {"A1": A1, "A2": A2, "A3": A3}
