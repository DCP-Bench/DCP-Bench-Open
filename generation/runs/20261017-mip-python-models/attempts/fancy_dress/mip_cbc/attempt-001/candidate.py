# Fancy dress party: Mr Greenguest wants the cheapest way to participate.
# Binary choices: tie t, hat h, shirt r, socks s, entrance fee n.
# Costs: tie 10, hat 2, socks 12, fee 11. The shirt is already owned, so r costs nothing.
import mip


def build(instance):
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    t = m.add_var("t", var_type=mip.BINARY)
    h = m.add_var("h", var_type=mip.BINARY)
    r = m.add_var("r", var_type=mip.BINARY)
    s = m.add_var("s", var_type=mip.BINARY)
    n = m.add_var("n", var_type=mip.BINARY)

    # 1 If someone wears a green tie he has to wear a green shirt.
    # Violated when t = 1 and r = 0.
    m.add_constr(n >= t - r)

    # 2 A guest may only wear green socks and a green shirt if he wears a green tie or a green hat.
    # Violated when s = 1, r = 1, t = 0 and h = 0.
    m.add_constr(n >= s + r - t - h - 1)

    # 3 A guest wearing a green shirt or a green hat or who does not wear green socks must wear a green tie.
    # Violated when (r or h or not s) and not t.
    m.add_constr(n >= r - t)
    m.add_constr(n >= h - t)
    m.add_constr(n >= 1 - s - t)

    # 4 A guest who is not dressed according to rules 1-3 must pay a $11 entrance fee.
    # The fee n is 1 whenever a rule above is violated; minimising the cost keeps n at 0 otherwise.
    m.objective = 10 * t + 2 * h + 12 * s + 11 * n

    return m, {"h": h, "n": n, "r": r, "s": s, "t": t}
