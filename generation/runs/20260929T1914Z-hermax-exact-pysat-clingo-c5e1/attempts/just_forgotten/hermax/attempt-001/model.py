# Just forgotten: Joe's account number uses each digit 0 to n-1 once. In each of
# several tried sets exactly some given number of digits are in the right place.
from hermax.model import Model


def build(instance):
    sets = instance["sets"]  # the digit sequences Joe tried
    num_correct = instance["num_correct_digits"]  # digits in the right place in each set
    n = len(sets[0])

    m = Model()
    # x[i] = the digit at position i of the account number
    x = m.int_vector("x", n, 0, n - 1)

    # each digit is used exactly once
    m &= m.vector([x[i] for i in range(n)]).all_different()

    # every tried set has exactly num_correct digits in the position they have in the number
    for tried in sets:
        m &= (sum(1 * (x[i] == tried[i]) for i in range(n)) == num_correct)

    return m, {"x": x}
