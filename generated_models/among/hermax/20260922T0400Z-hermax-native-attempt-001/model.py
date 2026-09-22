# Exactly m of the n variables take a value from v.
from hermax.model import Model


def build(instance):
    n = instance["n"]
    wanted = instance["m"]
    values = instance["v"]

    m = Model()
    # 0..7 is the domain the problem statement fixes, not an instance field.
    x = m.int_vector("x", n, 0, 7)
    # `x[i] == value` reifies to a literal, so the count is a plain sum.
    m &= (sum((x[i] == value) for i in range(n)
              for value in values if 0 <= value <= 7) == wanted)
    return m, {"x": x}
