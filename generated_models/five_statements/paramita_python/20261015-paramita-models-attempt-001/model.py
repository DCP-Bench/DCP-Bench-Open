# Five statements: statement i (1..5) says "exactly i of these statements are false".
# Equivalently, statement i is true exactly when the number of true statements is 5 - i.
from paramita.modelling import Bool, Iff


def build(instance):
    n = 5
    # s[i] = 1 if statement i+1 is true
    s = [Bool(f"s_{i}") for i in range(n)]
    cons = []
    # statement i+1 holds iff exactly i+1 statements are false, i.e. exactly 4 - i are true
    for i in range(n):
        cons.append(Iff(s[i], sum(s) == n - 1 - i))
    return cons, {"statements": s}
