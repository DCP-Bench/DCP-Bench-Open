# Hosting a dinner party: seat six guests (0 Andrew, 1 Betty, 2 Cara, 3 Dave,
# 4 Erica, 5 Frank) around a round table so that no two guests who do not get
# along sit next to each other. Output x is the seating order.
# The description asks to minimise conflicts; a seating with no conflict exists
# (the "get along" pairs form the cycle Andrew-Dave-Erica-Betty-Cara-Frank-Andrew),
# so the brief's satisfaction form is modelled: every neighbouring pair must be
# a compatible pair.
import mip

# Guests each one will sit next to (from the description).
NEIGHBOURS = {
    0: [3, 5],  # Andrew will only sit next to Dave and Frank
    1: [2, 4],  # Betty will only sit next to Cara and Erica
    2: [1, 5],  # Cara will only sit next to Betty and Frank
    3: [0, 4],  # Dave will only sit next to Andrew and Erica
    4: [1, 3],  # Erica will only sit next to Betty and Dave
    5: [0, 2],  # Frank will only sit next to Andrew and Cara
}


def build(instance):
    n = len(NEIGHBOURS)
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # p[i][g] = 1 when seat i holds guest g.
    p = [[model.add_var(f"p_{i}_{g}", var_type=mip.BINARY) for g in range(n)]
         for i in range(n)]

    # Each seat holds exactly one guest.
    # Each guest sits in exactly one seat.
    for i in range(n):
        model.add_constr(mip.xsum(p[i][g] for g in range(n)) == 1)
    for g in range(n):
        model.add_constr(mip.xsum(p[i][g] for i in range(n)) == 1)

    # If two guests who do not get along are seated next to each other, it will
    # create conflict at dinner. The table is round: seat i sits next to seat
    # (i + 1) mod n. If seat i holds guest g, then seat i + 1 must hold one of
    # the guests g will sit next to.
    for i in range(n):
        j = (i + 1) % n
        for g in range(n):
            model.add_constr(
                mip.xsum(p[j][h] for h in NEIGHBOURS[g]) >= p[i][g]
            )

    # Output: the guest number in each seat.
    x = [mip.xsum(g * p[i][g] for g in range(n)) for i in range(n)]
    return model, {"x": x}
