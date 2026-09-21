# Pick exactly m of the given integers so that they sum to zero.
from dcp_sat import Sat


def build(instance):
    nums = instance["nums"]
    wanted = instance["m"]

    sat = Sat()
    indices = sat.bools(len(nums))
    sat.bool_sum_eq(nums, indices, 0)
    sat.exactly(indices, wanted)
    return sat, {"indices": indices}
