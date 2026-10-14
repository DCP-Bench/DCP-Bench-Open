# ISBN-13: fill in the unknown digits (marked -1) of a 13-digit ISBN so that it is valid.
# It starts with 978 or 979 and its last digit is the check digit of the first twelve.
from pychoco.model import Model

UNKNOWN = -1  # marks an unknown digit in the instance


def build(instance):
    isbn_init = instance["isbn_init"]  # the digits, with -1 for the ones to find
    n = len(isbn_init)  # 13 digits

    model = Model()

    # isbn[i] = the i-th digit
    isbn = [model.intvar(0, 9, name=f"isbn_{i}") for i in range(n)]

    # the digits that are known
    for i in range(n):
        if isbn_init[i] != UNKNOWN:
            model.arithm(isbn[i], "=", isbn_init[i]).post()

    # an ISBN-13 starts with 978 or 979
    model.arithm(isbn[0], "=", 9).post()
    model.arithm(isbn[1], "=", 7).post()
    model.member(isbn[2], [8, 9]).post()

    # check digit: the first twelve digits are weighted alternately 1 and 3 and summed;
    # the check digit is (10 - (sum mod 10)) mod 10
    weights = [1 if i % 2 == 0 else 3 for i in range(n - 1)]
    weighted_sum = model.intvar(0, 9 * sum(weights), name="weighted_sum")
    model.scalar(isbn[: n - 1], weights, "=", weighted_sum).post()
    remainder = model.intvar(0, 9, name="remainder")  # sum mod 10
    model.mod(weighted_sum, 10, remainder).post()
    complement = model.intvar(1, 10, name="complement")  # 10 - (sum mod 10)
    model.arithm(remainder, "+", complement, "=", 10).post()
    model.mod(complement, 10, isbn[n - 1]).post()

    return model, {"isbn": isbn}
