# Problem: five_statements. Determine which of five statements is true.
# Statement i (i = 1..5) says: "Exactly i of these statements are false."
# Output statements[k] is 1 when statement k+1 is true, 0 otherwise.

import cvc5.pythonic as cz


def build(instance):
    s = cz.Bools("s1 s2 s3 s4 s5")
    # Number of false statements.
    num_false = cz.Sum([cz.If(cz.Not(b), 1, 0) for b in s])

    # Each statement is true exactly when the number of false statements equals its index.
    # Exactly one of these statements is false.
    # Exactly two of these statements are false.
    # Exactly three of these statements are false.
    # Exactly four of these statements are false.
    # Exactly five of these statements are false.
    constraints = [s[i] == (num_false == i + 1) for i in range(5)]

    return constraints, {"statements": list(s)}
