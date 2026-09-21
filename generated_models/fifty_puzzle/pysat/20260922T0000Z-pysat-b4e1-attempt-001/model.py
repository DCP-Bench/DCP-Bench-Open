# Knock over the dummies whose numbers add up to exactly the target.
from dcp_sat import Sat


def build(instance):
    values = instance["values"]
    target = instance["target_sum"]

    sat = Sat()
    dummies = sat.bools(len(values))
    sat.bool_sum_eq(values, dummies, target)
    return sat, {"dummies": dummies}
