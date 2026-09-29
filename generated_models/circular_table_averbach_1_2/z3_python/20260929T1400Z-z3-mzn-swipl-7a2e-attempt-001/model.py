# Averbach's card-passing riddle: three players X, Y, Z of three different
# nationalities (American, English, French) sit round a table, each passing
# three cards to the person on their right. Y passed to the American, and X
# passed to the person who passed to the Frenchwoman. Find who is who.
# A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
import z3


def build(instance):
    # The riddle fixes everything; the instance carries no data.
    solver = z3.Solver()

    # seats of the three players, all different
    x, y, z = z3.Ints("x y z")
    for seat in (x, y, z):
        solver.add(seat >= 0, seat <= 2)
    solver.add(z3.Distinct(x, y, z))

    # seats of the three nationalities, all different: the same seat number in
    # the player and nationality outputs denotes the same person
    american, english, french = z3.Ints("american english french")
    for seat in (american, english, french):
        solver.add(seat >= 0, seat <= 2)
    solver.add(z3.Distinct(american, english, french))

    def right_to(a, b):
        """The seat a is immediately to the right of the seat b."""
        return a == (b + 1) % 3

    # the American sits to the right of Y, since Y passed to the American
    solver.add(right_to(american, y))
    # X sits to the right of the Frenchwoman, since X passed to the person who passed to her
    solver.add(right_to(x, french))

    return solver, {"x": x, "y": y, "z": z, "american": american, "english": english, "french": french}
