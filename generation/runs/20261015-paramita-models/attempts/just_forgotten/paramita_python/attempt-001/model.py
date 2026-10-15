# Just forgotten: Joe's account number is a permutation of the digits 0 to n-1, and each
# set he tried has exactly num_correct_digits digits in their correct position.
from paramita.modelling import Bool


def build(instance):
    sets = instance["sets"]  # each set is a permutation of 0..n-1
    k = instance["num_correct_digits"]
    n = len(sets[0])

    # One-hot encoding of the account number: xv[i][v] is true when digit v is at position i.
    xv = [[Bool(f"x_{i}_{v}") for v in range(n)] for i in range(n)]
    cons = []

    # The account number has all the digits from 0 to n-1 in some order.
    # Each position holds exactly one digit.
    cons += [sum(xv[i]) == 1 for i in range(n)]
    # Each digit is used at exactly one position.
    cons += [sum(xv[i][v] for i in range(n)) == 1 for v in range(n)]

    # In each set, just num_correct_digits digits are in their correct position.
    # Position i of the set is correct when the account number has the same digit there.
    for s in sets:
        cons.append(sum(xv[i][s[i]] for i in range(n)) == k)

    x = [sum(v * xv[i][v] for v in range(n)) for i in range(n)]
    return cons, {"x": x}
