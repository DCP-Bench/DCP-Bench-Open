# Just forgotten: Joe's account number uses each digit 0..n-1 once. In every one of his
# tried sets exactly a given number of the digits are in their correct position.
# Find the account number.
from pychoco.model import Model


def build(instance):
    sets = instance["sets"]  # the sets of digits Joe tried
    num_correct_digits = instance["num_correct_digits"]  # digits in the right place in every set
    n = len(sets[0])

    model = Model()

    # x[i] = the i-th digit of the account number
    x = [model.intvar(0, n - 1, name=f"x_{i}") for i in range(n)]

    # all the digits from 0 to n - 1 are used, in some order
    model.all_different(x).post()

    # in each tried set exactly num_correct_digits digits are in their correct position
    for tried in sets:
        in_place = [model.arithm(x[i], "=", tried[i]).reify() for i in range(n)]
        model.sum(in_place, "=", num_correct_digits).post()

    return model, {"x": x}
