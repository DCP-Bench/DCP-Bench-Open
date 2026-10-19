# Handshaking problem (Halmos): Hilary and Jocelyn are married and invite
# num_couples couples. Everyone shakes hands, but nobody shakes hands with
# themselves or with their spouse. Jocelyn asks each person how many hands they
# shook, and all the answers are different. Output: the number of hands Hilary shook.
import cvc5.pythonic as cz


def build(instance):
    n = instance["num_couples"]
    # Person 0 is Hilary, person 1 is Jocelyn, then the invited couples as (2k, 2k+1).
    people = 2 * n + 2

    def spouse(i):
        return i ^ 1

    # One Boolean per unordered pair: True when the two shake hands.
    h = {}
    for i in range(people):
        for j in range(i + 1, people):
            h[(i, j)] = cz.Bool(f"h_{i}_{j}")

    def hand(i, j):
        return h[(i, j)] if i < j else h[(j, i)]

    constraints = []

    # Nobody shakes hands with his or her spouse.
    for (i, j), b in h.items():
        if spouse(i) == j:
            constraints.append(cz.Not(b))

    # The number of hands each person has shaken: the handshakes with the others.
    # Nobody shakes hands with him or herself, so a person's own pair is skipped.
    counts = []
    for i in range(people):
        counts.append(cz.Sum([cz.If(hand(i, j), 1, 0) for j in range(people) if j != i]))

    # All the answers are different. Jocelyn asks the others, so her own count is left out.
    answers = [counts[i] for i in range(people) if i != 1]
    constraints.append(cz.Distinct(answers))

    return constraints, {"hil": counts[0]}
