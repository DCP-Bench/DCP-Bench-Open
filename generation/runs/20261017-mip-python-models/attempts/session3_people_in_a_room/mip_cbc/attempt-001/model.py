# People in a room: 13 people enter a room one at a time, 4 of them male and
# 9 female. Find an order of entry where the ratio of females to males in the
# room at any one time is no greater than 7/3. Output `sequence`: entry i is
# 1 for a female and 0 for a male.
import mip


def build(instance):
    n = 13
    males = 4
    females = n - males
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = [model.add_var(f"f_{i}", var_type=mip.BINARY) for i in range(n)]

    # 4 of them are male, so the other 9 are female.
    model.add_constr(mip.xsum(x) == females)

    # The ratio of females to males in the room at any one time is no greater
    # than 7/3, so 3 * females <= 7 * males after each entry (this also forces
    # the room to have no females while it has no males).
    for t in range(n):
        f_t = mip.xsum(x[: t + 1])
        m_t = (t + 1) - f_t
        model.add_constr(3 * f_t <= 7 * m_t)

    return model, {"sequence": x}
