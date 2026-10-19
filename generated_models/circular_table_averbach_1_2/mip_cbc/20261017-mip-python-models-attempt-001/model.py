# Circular table of Hearts players: three seats 0, 1, 2 around a round table.
# Seat 1 is right of seat 0, seat 2 is right of seat 1, and seat 0 is right of seat 2,
# so the seat on the right of seat p is (p + 1) mod 3.
# Players X, Y, Z of different nationalities (American, English, French) sit one per seat.
# Output: x, y, z are the seats of the players; american, english, french are the seats of the nationalities.
import mip

SEATS = 3
PEOPLE = ["x", "y", "z"]
NATIONS = ["american", "english", "french"]
ALL = PEOPLE + NATIONS


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    out = {}
    seat_of = {}
    for name in ALL:
        out[name] = model.add_var(name, lb=0, ub=SEATS - 1, var_type=mip.INTEGER)
        seat_of[name] = [model.add_var(f"{name}_at_{s}", var_type=mip.BINARY) for s in range(SEATS)]

    # Each player and each nationality sits in exactly one seat, and the output value is that seat.
    for name in ALL:
        model.add_constr(mip.xsum(seat_of[name]) == 1)
        model.add_constr(out[name] == mip.xsum(s * seat_of[name][s] for s in range(SEATS)))

    # Each seat holds exactly one of the three players and exactly one of the three nationalities.
    for s in range(SEATS):
        model.add_constr(mip.xsum(seat_of[p][s] for p in PEOPLE) == 1)
        model.add_constr(mip.xsum(seat_of[n][s] for n in NATIONS) == 1)

    # Y passed three hearts to the American: the American sits on the right of Y.
    for s in range(SEATS):
        model.add_constr(seat_of["american"][(s + 1) % SEATS] == seat_of["y"][s])

    # X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman:
    # that person sits on the right of X, and the Frenchwoman sits on the right of that person,
    # so the Frenchwoman sits two seats to the right of X.
    for s in range(SEATS):
        model.add_constr(seat_of["french"][(s + 2) % SEATS] == seat_of["x"][s])

    return model, out
