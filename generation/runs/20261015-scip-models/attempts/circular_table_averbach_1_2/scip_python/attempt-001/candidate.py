# Circular table (Averbach 1.2): three players X, Y, Z of American, English and
# French nationality sit around a table playing Hearts; find who is who.
from pyscipopt import Model, quicksum

# Seats are numbered 0, 1, 2 around the table; seat 1 is right of seat 0, seat 2
# is right of seat 1, and seat 0 is right of seat 2. The right-hand neighbour of
# seat s is seat (s + 1) % 3. The output value of each person and nationality is
# the seat it occupies, so the same value matches a person to a nationality.
SEATS = range(3)
PEOPLE = ["x", "y", "z"]
NATIONS = ["american", "english", "french"]


def build(instance):
    m = Model()

    # sit[p, s] = 1 if person p sits at seat s
    sit = {(p, s): m.addVar(name=f"sit_{p}_{s}", vtype="B") for p in PEOPLE for s in SEATS}
    # nat[n, s] = 1 if the person of nationality n sits at seat s
    nat = {(n, s): m.addVar(name=f"nat_{n}_{s}", vtype="B") for n in NATIONS for s in SEATS}

    # every person has one seat, every seat has one person
    for p in PEOPLE:
        m.addCons(quicksum(sit[p, s] for s in SEATS) == 1, name=f"one_seat_{p}")
    for s in SEATS:
        m.addCons(quicksum(sit[p, s] for p in PEOPLE) == 1, name=f"one_person_at_{s}")

    # every nationality has one seat, every seat has one nationality
    for n in NATIONS:
        m.addCons(quicksum(nat[n, s] for s in SEATS) == 1, name=f"one_seat_{n}")
    for s in SEATS:
        m.addCons(quicksum(nat[n, s] for n in NATIONS) == 1, name=f"one_nation_at_{s}")

    # Y passed three hearts to the American: the American sits right of Y
    for s in SEATS:
        m.addCons(sit["y", s] <= nat["american", (s + 1) % 3],
                  name=f"y_passed_to_american_{s}")

    # X passed the queen of spades and two diamonds to the person who passed
    # their cards to the Frenchwoman. X passes to the seat on the right, which
    # passes to the seat after that, where the Frenchwoman sits.
    for s in SEATS:
        m.addCons(sit["x", s] <= nat["french", (s + 2) % 3],
                  name=f"x_passed_via_to_french_{s}")

    outputs = {
        "x": quicksum(s * sit["x", s] for s in SEATS),
        "y": quicksum(s * sit["y", s] for s in SEATS),
        "z": quicksum(s * sit["z", s] for s in SEATS),
        "american": quicksum(s * nat["american", s] for s in SEATS),
        "english": quicksum(s * nat["english", s] for s in SEATS),
        "french": quicksum(s * nat["french", s] for s in SEATS),
    }
    return m, outputs
