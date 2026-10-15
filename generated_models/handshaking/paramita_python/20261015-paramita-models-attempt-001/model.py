from paramita.modelling import Bool

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

    # Hands counted per person as a one-hot value over 0..max_hands.
    # Jocelyn (person 1) asks everyone else, so she has no one-hot.
    asked = [p for p in range(people) if p != 1]
    oh = {}
    for p in asked:
        oh[p] = {v: Bool(f"hands_{p}_is_{v}") for v in range(max_hands + 1)}
        # each person has exactly one number of hands
        cons.append(sum(oh[p].values()) == 1)
        # the one-hot value is that person's handshake count
        cons.append(hands(p) == sum(v * oh[p][v] for v in range(max_hands + 1)))

    # All answers are different: each number of hands is given to at most
    # one asked person. There are 2n+1 asked people and 2n+1 possible
    # counts (0..2n), so each count is given to exactly one person.
    for v in range(max_hands + 1):
        cons.append(sum(oh[p][v] for p in asked) == 1)

    # Hilary (person 0) has shaken how many hands: the number to print.
    hil = hands(0)
    return cons, {"hil": hil}
