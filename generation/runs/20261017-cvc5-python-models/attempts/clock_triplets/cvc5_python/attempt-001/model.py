# Clock triplets: rearrange the numbers 1 to 12 on the face of a clock so that
# no triplet of adjacent numbers has a sum higher than 21.
# Output x: the arrangement of the numbers on the clock, as 12 integers.
import cvc5.pythonic as cz

N = 12
MAX_TRIPLET_SUM = 21


def build(instance):
    x = [cz.Int(f"x_{i}") for i in range(N)]
    constraints = []

    # Rearrange the numbers 1 to 12 on the face of the clock: each position holds
    # one number from 1 to 12, and every number is used exactly once.
    for v in x:
        constraints.append(v >= 1)
        constraints.append(v <= N)
    constraints.append(cz.Distinct(x))

    # No triplet of adjacent numbers has a sum higher than 21. The clock is a circle,
    # so the triplets wrap around from the last position back to the first.
    for i in range(N):
        constraints.append(x[i] + x[(i + 1) % N] + x[(i + 2) % N] <= MAX_TRIPLET_SUM)

    return constraints, {"x": x}
