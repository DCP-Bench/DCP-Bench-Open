from paramita.modelling import Bool

# Thirteen people enter a room one at a time. x[i] is True when the person
# entering at position i is female (0 = male, 1 = female).
N_PEOPLE = 13
N_MALES = 4


def build(instance):
    x = [Bool(f"female_{i}") for i in range(N_PEOPLE)]
    cons = []

    # There are 13 people, 4 of them are male: exactly 9 females in total.
    cons.append(sum(x) == N_PEOPLE - N_MALES)

    # The ratio of females to males in the room at any one time is no greater
    # than 7/3: for every prefix of k entries, females / males <= 7 / 3, i.e.
    # 3 * females <= 7 * males, where males = k - females. This forces the
    # first person to be male, since a single female with no males is not allowed.
    for k in range(1, N_PEOPLE + 1):
        # ratio of females to males at time k is at most 7/3
        cons.append(sum(10 * b for b in x[:k]) <= 7 * k)

    return cons, {"sequence": x}
