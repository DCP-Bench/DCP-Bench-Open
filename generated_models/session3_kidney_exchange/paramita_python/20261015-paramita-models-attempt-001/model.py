# Kidney exchange: n people on a waiting list; compatible[i] is the set of people that
# person i can donate a kidney to. Find the transplants that maximise the number of people
# who receive a new kidney, where anyone who gives a kidney must receive one and no person
# receives more than one kidney. Output: transplants[i][j] is 1 if person i donates to
# person j, and 0 otherwise.
#
# Encoding: one Bool x[i][j] per ordered pair of people, meaning "i donates to j". Pairs
# that are not in the compatibility lists are forced false. The compatibility lists in the
# instance use 1-based person numbers; the matrix uses 0-based indices (person p is row p-1).
from paramita.modelling import Bool


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]

    # x[i][j] = 1 if person i donates a kidney to person j
    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    cons = []
    # a person cannot donate to himself or herself
    cons += [~x[i][i] for i in range(n)]
    # a donation is only possible to a person in the donor's compatibility list
    allowed = [set(v - 1 for v in compatible[i]) for i in range(n)]
    cons += [~x[i][j] for i in range(n) for j in range(n) if j != i and j not in allowed[i]]

    # no person donates more than one kidney
    cons += [sum(x[i][j] for j in range(n)) <= 1 for i in range(n)]
    # no person receives more than one kidney
    cons += [sum(x[i][j] for i in range(n)) <= 1 for j in range(n)]
    # anyone who gives a kidney must receive one: the number of kidneys a person gives
    # is at most the number of kidneys the person receives
    cons += [sum(x[i][j] for j in range(n)) - sum(x[k][i] for k in range(n)) <= 0 for i in range(n)]

    # maximise the number of people who receive a new kidney, which is the number of
    # donations, since each receiver receives from exactly one donor
    total = sum(x[i][j] for i in range(n) for j in range(n))

    return cons, {"transplants": x}, ("maximize", total)
