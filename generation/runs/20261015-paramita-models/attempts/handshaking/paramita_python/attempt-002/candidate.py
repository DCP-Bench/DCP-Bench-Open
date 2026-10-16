from paramita.modelling import Bool, If, Iff

# Hilary and Jocelyn are married. They invite num_couples couples who are
# friends for dinner. Persons 2k and 2k+1 are a couple; couple 0 is Hilary
# (person 0) and Jocelyn (person 1). Persons 2..2n+1 are the invited guests.


def build(instance):
    n = instance["num_couples"]
    people = 2 * (n + 1)
    max_hands = people - 2  # everyone except self and spouse
    cons = []

    def spouse(p):
        return p ^ 1

    # Shake bools exist only for pairs that are neither the same person nor
    # married to each other. The pair (i, j) with i < j is one Bool; the
    # handshake is symmetric.
    shake = {}
    for i in range(people):
        for j in range(i + 1, people):
            if j != spouse(i):
                shake[(i, j)] = Bool(f"shake_{i}_{j}")

    def hands(p):
        # number of hands person p has shaken
        return sum(
            shake[(min(p, q), max(p, q))]
            for q in range(people)
            if q != p and q != spouse(p)
        )

    # Jocelyn (person 1) asks everyone else, so she has no count to distinguish.
    asked = [p for p in range(people) if p != 1]

    # Unary (order) encoding of each asked person's hand count: ge[p][k] is true
    # exactly when person p has shaken at least k hands, for k = 1..2n.
    ge = {p: {k: Bool(f"hands_{p}_at_least_{k}") for k in range(1, max_hands + 1)} for p in asked}
    for p in asked:
        for k in range(1, max_hands + 1):
            cons.append(Iff(ge[p][k], hands(p) >= k))
            if k < max_hands:
                # a count of at least k+1 implies at least k
                cons.append(If(ge[p][k + 1], ge[p][k]))

    # All answers are different. The asked people have counts 0..2n (2n+1
    # values for 2n+1 people), so each count is used exactly once. Equivalently,
    # the number of asked people with at least k hands is the number of values
    # from k to 2n, which is 2n+1-k.
    for k in range(1, max_hands + 1):
        cons.append(sum(ge[p][k] for p in asked) == max_hands + 1 - k)

    # Hilary (person 0) has shaken how many hands: the number to print.
    hil = hands(0)
    return cons, {"hil": hil}
