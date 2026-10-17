# Model for eighteen_hole_golf: a random 18-hole golf course where each hole
# has a length of 3, 4, or 5, and the total length of the course is 72.
# Output: holes, the lengths of the 18 holes.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    # Each hole has a length of 3, 4, or 5.
    holes = [model.add_var(f"hole_{i}", lb=3, ub=5, var_type=mip.INTEGER)
             for i in range(18)]
    # The total length of the course is 72.
    model += mip.xsum(holes) == 72
    return model, {"holes": holes}
