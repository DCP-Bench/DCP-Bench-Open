# Rectangular packing: place n axis-parallel rectangles (widths[i] x heights[i]) into a
# container of size total_x x total_y without overlap and with every rectangle inside the
# container. Rectangles are not rotated. Minimise the container area total_x * total_y.
import mip


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)
    # Bounds from the data: the rectangles side by side need sum(widths) by max(heights),
    # so a container never needs a side longer than the sum of the item sides.
    sum_w = sum(widths)
    sum_h = sum(heights)
    max_w = max(widths)
    max_h = max(heights)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Lower-left corner of rectangle i (0-based), left edge in 0..sum_w - widths[i].
    pos_x = [model.add_var(name=f"pos_x_{i}", lb=0, ub=sum_w - widths[i], var_type=mip.INTEGER)
             for i in range(n)]
    pos_y = [model.add_var(name=f"pos_y_{i}", lb=0, ub=sum_h - heights[i], var_type=mip.INTEGER)
             for i in range(n)]

    # Container dimensions.
    total_x = model.add_var(name="total_x", lb=max_w, ub=sum_w, var_type=mip.INTEGER)
    total_y = model.add_var(name="total_y", lb=max_h, ub=sum_h, var_type=mip.INTEGER)

    # The container width is one value from max_w..sum_w, chosen by one binary per value.
    # The objective is total_x * total_y, which is not linear, so the height is multiplied
    # in per width value: area_part[a] = total_y when width a is chosen, else 0.
    width_values = list(range(max_w, sum_w + 1))
    width_choice = {a: model.add_var(name=f"width_is_{a}", var_type=mip.BINARY) for a in width_values}
    area_part = {a: model.add_var(name=f"area_part_{a}", lb=0, ub=sum_h) for a in width_values}

    # the container width is exactly one of the candidate values
    model += mip.xsum(width_choice.values()) == 1
    model += total_x == mip.xsum(a * width_choice[a] for a in width_values)
    for a in width_values:
        # area_part[a] <= total_y, and area_part[a] = total_y when width a is chosen
        model += area_part[a] <= total_y
        model += area_part[a] <= sum_h * width_choice[a]
        model += area_part[a] >= total_y - sum_h * (1 - width_choice[a])

    # the container area is total_x * total_y
    model.objective = mip.xsum(a * area_part[a] for a in width_values)

    # every item lies within the container: its right edge and its top edge do not exceed it
    for i in range(n):
        model += pos_x[i] + widths[i] <= total_x
        model += pos_y[i] + heights[i] <= total_y

    # no two items overlap: for each pair, one of four separations holds (item i left of j,
    # item j left of i, item i below j, item j below i), chosen by four binaries
    for i in range(n):
        for j in range(i + 1, n):
            left = model.add_var(name=f"left_{i}_{j}", var_type=mip.BINARY)
            right = model.add_var(name=f"right_{i}_{j}", var_type=mip.BINARY)
            below = model.add_var(name=f"below_{i}_{j}", var_type=mip.BINARY)
            above = model.add_var(name=f"above_{i}_{j}", var_type=mip.BINARY)
            # the items do not overlap: at least one separation holds
            model += mip.xsum([left, right, below, above]) >= 1
            # item i left of item j (big-M = sum_w, the largest possible horizontal gap)
            model += pos_x[i] - pos_x[j] + sum_w * left <= sum_w - widths[i]
            # item j left of item i
            model += pos_x[j] - pos_x[i] + sum_w * right <= sum_w - widths[j]
            # item i below item j (big-M = sum_h, the largest possible vertical gap)
            model += pos_y[i] - pos_y[j] + sum_h * below <= sum_h - heights[i]
            # item j below item i
            model += pos_y[j] - pos_y[i] + sum_h * above <= sum_h - heights[j]

    outputs = {
        "pos_x": pos_x,
        "pos_y": pos_y,
        "total_x": total_x,
        "total_y": total_y,
    }
    return model, outputs
