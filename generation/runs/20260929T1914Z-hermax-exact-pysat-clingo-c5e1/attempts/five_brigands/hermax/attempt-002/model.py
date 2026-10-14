# Five brigands: Alfonso, Benito, Carlos, Diego and Esteban share 200 doubloons,
# each has at least one, and the total would still be 200 if Alfonso had twelve
# times as much, Benito three times, Carlos the same, Diego half and Esteban a third.
from hermax.model import Model

# 12A + 3B + C + D/2 + E/3 = 200, multiplied by 6 to get whole numbers
TIMES_SIX = {"A": 72, "B": 18, "C": 6, "D": 3, "E": 2}


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    m = Model()
    # A share is at least 1. In the second condition the others take at least their
    # coefficient each, which caps a share at (1200 - the others) / its coefficient.
    total_coefficients = sum(TIMES_SIX.values())
    share = {name: m.int(name, 1, min(200, (1200 - (total_coefficients - c)) // c))
             for name, c in TIMES_SIX.items()}

    # The two conditions are built as sums of scaled shares (an adder network), which
    # this solver handles far better than a weighted equality over the shares.
    # Together they have 200 doubloons.
    total = m.sum_var([m.scale(share[name], 1) for name in TIMES_SIX])
    m &= (total == 200)
    # With the changed amounts they would still have 200 (times 6).
    changed_total = m.sum_var([m.scale(share[name], c) for name, c in TIMES_SIX.items()])
    m &= (changed_total == 1200)

    return m, share
