# ISBN-13 validation and check digit calculation.
# An ISBN-13 has 13 digits; -1 in the instance marks an unknown digit.
# Find the unknown digits so that the number is a valid ISBN-13.
import cvc5.pythonic as cz


def build(instance):
    init = instance["isbn_init"]
    n = 13
    d = cz.Ints(" ".join(f"d{i}" for i in range(n)))
    constraints = []

    # Each digit is between 0 and 9.
    # Digits given in the instance are fixed; -1 marks an unknown digit.
    # Every digit is a decimal digit.
    for i in range(n):
        constraints.append(d[i] >= 0)
        constraints.append(d[i] <= 9)
    for i in range(n):
        if init[i] != -1:
            constraints.append(d[i] == init[i])

    # An ISBN-13 must start with 978 or 979.
    constraints.append(d[0] == 9)
    constraints.append(d[1] == 7)
    constraints.append(cz.Or(d[2] == 8, d[2] == 9))

    # Multiply the digits alternately by 1 and 3, starting with 1.
    # Sum the products. The weighted sum of all 13 digits must be divisible by 10.
    # This is equivalent to check digit = (10 - (sum of first 12 weighted digits) % 10) % 10.
    weighted = [d[i] if i % 2 == 0 else 3 * d[i] for i in range(n)]
    total = cz.Sum(weighted)
    constraints.append(total % 10 == 0)

    outputs = {"isbn": [d[i] for i in range(n)]}
    return constraints, outputs
