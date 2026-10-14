# Bank card: find the four-digit PIN abcd with no repeated digit, where the two-digit number
# cd is three times ab, and da is two times bc.
from hermax.model import Model


def build(instance):
    # The facts are fixed by the problem; the instance carries no data.
    m = Model()
    # the four digits of the PIN
    a, b, c, d = (m.int(name, 0, 9) for name in "abcd")

    # no two digits are the same
    m &= m.vector([a, b, c, d]).all_different()
    # the 2-digit number cd is 3 times the 2-digit number ab
    m &= (10 * c + d == 30 * a + 3 * b)
    # the 2-digit number da is 2 times the 2-digit number bc
    m &= (10 * d + a == 20 * b + 2 * c)

    return m, {"a": a, "b": b, "c": c, "d": d}
