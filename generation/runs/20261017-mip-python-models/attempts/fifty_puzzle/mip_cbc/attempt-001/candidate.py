# Fifty puzzle (Loyd's dummies): choose a subset of dummies whose numbers add up
# to exactly the target sum. Output "dummies" is a Boolean per dummy, true when knocked over.
import mip


def build(instance):
    values = instance["values"]
    target = instance["target_sum"]
    n = len(values)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    dummies = [model.add_var(f"d_{i}", var_type=mip.BINARY) for i in range(n)]

    # The numbers on the men knocked down add up to exactly the target sum.
    model += mip.xsum(values[i] * dummies[i] for i in range(n)) == target

    return model, {"dummies": dummies}
