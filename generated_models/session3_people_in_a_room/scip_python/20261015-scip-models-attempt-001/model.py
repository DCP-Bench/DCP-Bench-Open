# People entering a room one at a time (13 people, 4 male, 9 female): order the
# entries so that the female/male ratio in the room is never greater than 7/3.
from pyscipopt import Model, quicksum

# The problem statement fixes the numbers of people and males; there are no instance fields.
N_PEOPLE = 13
N_MALES = 4


def build(instance):
    m = Model()
    # x[t] = 1 if the person entering at position t is female, 0 if male
    x = [m.addVar(name=f"female_{t}", vtype="B") for t in range(N_PEOPLE)]

    # the room holds 4 males and 9 females in total
    # exactly the stated number of males enter
    m.addCons(quicksum(x) == N_PEOPLE - N_MALES)

    # the ratio of females to males in the room is at most 7/3 at every time:
    # F / M <= 7 / 3, written as 3 F <= 7 M, with F = females so far and M = males so far
    # (M = t + 1 - F after t + 1 entries, so this becomes 10 F <= 7 (t + 1))
    # with no males in the room, any female already breaks the ratio
    for t in range(N_PEOPLE):
        m.addCons(quicksum(10 * x[s] for s in range(t + 1)) <= 7 * (t + 1))

    # the output lists the sequence of entries, 0 for male and 1 for female
    return m, {"sequence": x}
