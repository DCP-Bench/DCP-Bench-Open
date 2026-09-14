import cpmpy as cp
import numpy as np


def build(instance):
    n = instance["n"]
    queens = cp.intvar(1, n, shape=n, name="queens")
    offsets = np.arange(n)
    model = cp.Model(
        cp.AllDifferent(queens),
        cp.AllDifferent(queens - offsets),
        cp.AllDifferent(queens + offsets),
    )
    return model, {"queens": [queens[i] for i in range(n)]}
