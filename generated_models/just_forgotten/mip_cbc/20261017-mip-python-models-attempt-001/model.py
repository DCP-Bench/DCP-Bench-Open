# Joe's bank account number x: a permutation of the digits 0..n-1, where n is the
# number of digits in each set. Each set is a permutation of the same digits and,
# for that set, exactly num_correct_digits positions hold the same digit as x.
# The output x is the account number as a list of n integers.
import mip


def build(instance):
    sets = instance["sets"]
    k = instance["num_correct_digits"]
    n = len(sets[0])
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # account number: n digits, each in 0..n-1
    x = [model.add_var(f"x_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER) for i in range(n)]

    # one-hot encoding: p[i][v] = 1 iff digit at position i is v
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in range(n)] for i in range(n)]

    # Joe's account number has all the digits from 0 to n-1 in some order
    for i in range(n):
        model += mip.xsum(p[i][v] for v in range(n)) == 1
        model += x[i] == mip.xsum(v * p[i][v] for v in range(n))
    for v in range(n):
        model += mip.xsum(p[i][v] for i in range(n)) == 1

    # in each set just a specific number of the digits were in their correct position
    for s in sets:
        model += mip.xsum(p[i][s[i]] for i in range(n)) == k

    return model, {"x": x}
