# Langford pairing problem (csplib 024): arrange the two copies of each number 1..k
# into one sequence of 2k positions so that the two copies of i are i+1 positions apart.
# The declared output sol is the sequence of 2k integers. Satisfaction problem.
import mip


def build(instance):
    k = instance["k"]
    n = 2 * k
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Placement binaries: x[(i, p)] = 1 when the first copy of i is at position p
    # and the second copy is at position p + i + 1.
    x = {}
    for i in range(1, k + 1):
        for p in range(0, n - i - 1):
            x[(i, p)] = m.add_var(f"x_{i}_{p}", var_type=mip.BINARY)

    # The two numbers 1..k: each number i has exactly one placement.
    # Every number i is placed exactly once, as a pair of copies i+1 apart.
    for i in range(1, k + 1):
        m += mip.xsum(x[(i, p)] for p in range(0, n - i - 1)) == 1

    # The sequence of 2k numbers: every position holds exactly one copy of some number.
    # A position q is covered by number i when it is the first or the second copy of i.
    sol = []
    for q in range(n):
        covers = []
        for i in range(1, k + 1):
            if (i, q) in x:
                covers.append((i, x[(i, q)]))
            if (i, q - i - 1) in x:
                covers.append((i, x[(i, q - i - 1)]))
        m += mip.xsum(b for _, b in covers) == 1
        # The number at position q: an integer variable tied to the placements by an equality row.
        s = m.add_var(f"sol_{q}", lb=1, ub=k, var_type=mip.INTEGER)
        m += s == mip.xsum(i * b for i, b in covers)
        sol.append(s)

    return m, {"sol": sol}
