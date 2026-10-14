# Fifty puzzle: knock over some of the dummies so that the numbers painted on
# the fallen ones add up to exactly the target sum.
from hermax.model import Model


def build(instance):
    target_sum = instance["target_sum"]  # the sum the knocked-over dummies must reach
    values = instance["values"]  # values[i] = number on dummy i
    n = len(values)

    m = Model()
    # dummies[i] = dummy i is knocked over
    dummies = m.bool_vector("dummies", n)

    # the numbers on the knocked-over dummies add up to exactly the target
    m &= (sum(values[i] * dummies[i] for i in range(n)) == target_sum)

    return m, {"dummies": dummies}
