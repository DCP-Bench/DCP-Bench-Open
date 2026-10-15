# Just forgotten: find Joe's account number, a permutation of the digits 0..n-1,
# given sets of digits where exactly k digits are in their correct position.
# Output: the account number x as a list of n integers.

from pyscipopt import Model, quicksum


def build(instance):
    sets = instance["sets"]
    k = instance["num_correct_digits"]
    n = len(sets[0])
    m = Model()

    # b[i, v] = 1 if the account number has digit v in position i
    b = {(i, v): m.addVar(name=f"b_{i}_{v}", vtype="B") for i in range(n) for v in range(n)}

    # each position holds exactly one digit
    for i in range(n):
        # position i has exactly one digit
        m.addCons(quicksum(b[i, v] for v in range(n)) == 1)

    # each digit is used exactly once
    for v in range(n):
        # digit v appears exactly once in the account number
        m.addCons(quicksum(b[i, v] for i in range(n)) == 1)

    # each tried set has exactly k digits in their correct position
    for s, digits in enumerate(sets):
        # set s matches the account number in exactly k positions
        m.addCons(quicksum(b[i, digits[i]] for i in range(n)) == k)

    # the output gives the digit at each position
    x = [quicksum(v * b[i, v] for v in range(n)) for i in range(n)]
    return m, {"x": x}
