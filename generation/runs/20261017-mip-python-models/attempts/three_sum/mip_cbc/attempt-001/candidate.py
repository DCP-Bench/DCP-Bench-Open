# Three-sum: given a collection of integers, find a number of elements that sum to zero.
# Print whether each element is selected (indices) as a list of booleans.
# Satisfaction problem. Instance fields: nums (list of integers), m (number of elements to select).
import mip


def build(instance):
    nums = instance["nums"]
    m_count = instance["m"]
    n = len(nums)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n)]

    # select a number of elements that sum to zero
    model += mip.xsum(x) == m_count
    model += mip.xsum(nums[i] * x[i] for i in range(n)) == 0

    return model, {"indices": x}
