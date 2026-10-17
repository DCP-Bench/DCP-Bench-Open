# Bus scheduling: Progress City wants the minimum number of buses so that the
# bus count covers the demand of each 4-hour interval of the day. Each bus works
# 8 successive hours, so it covers two successive intervals, and the day wraps
# around (shifts overlap across the end of the day).
import mip


def build(instance):
    demands = instance["demands"]
    n = len(demands)
    max_d = max(demands) if demands else 0

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i]: number of buses that start their 8-hour shift in interval i.
    # A bus starting in interval i covers intervals i and i+1 (cyclically).
    # An optimal schedule never starts more than max(demands) buses in one
    # interval: reducing such a count keeps every demand covered.
    x = [model.add_var(f"x_{i}", lb=0, ub=max_d, var_type=mip.INTEGER) for i in range(n)]

    # Each 4-hour interval must have enough buses on duty to meet its demand.
    # Buses on duty in interval i are those starting in i or in the interval before it.
    # the number of buses available in each 4-hour interval meets the demand for that interval
    for i in range(n):
        model += x[i] + x[(i - 1) % n] >= demands[i]

    # Minimise the total number of buses.
    # the minimum number of buses required to meet the transportation needs throughout the day
    model.objective = mip.xsum(x)

    return model, {"x": x}
