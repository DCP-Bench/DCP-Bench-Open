# Just forgotten: find Joe's account number x, a permutation of the digits 0 to n-1,
# given several guessed sets. Each set is a permutation of 0 to n-1 and in each set
# exactly num_correct_digits digits are in their correct position compared with x.
import cvc5.pythonic as cz


def build(instance):
    sets = instance["sets"]
    k = instance["num_correct_digits"]
    n = len(sets[0])

    x = [cz.Int(f"x{i}") for i in range(n)]
    constraints = []

    # the account number has all the digits from 0 to n-1 in some order
    constraints += [x[i] >= 0 for i in range(n)]
    constraints += [x[i] <= n - 1 for i in range(n)]
    constraints.append(cz.Distinct(x))

    # in each set just a specific number of the digits were in their correct position
    for s in sets:
        constraints.append(
            cz.Sum([cz.If(x[i] == s[i], 1, 0) for i in range(n)]) == k
        )

    return constraints, {"x": x}
