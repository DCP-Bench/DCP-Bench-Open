# Averbach's card-passing riddle: three players X, Y, Z of three different
# nationalities (American, English, French) sit round a table, each passing
# three cards to the person on their right. Y passed to the American, and X
# passed to the person who passed to the Frenchwoman. Find who is who.
# A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The riddle fixes everything; the instance carries no data.
    pool = IDPool()
    names = ["x", "y", "z", "american", "english", "french"]
    seats = {name: Integer(name, 0, 2, vpool=pool) for name in names}
    engine = IntegerEngine(vars=list(seats.values()), vpool=pool)

    # seats of the three players are all different, and so are the nationalities'
    # (the same seat number in the player and nationality outputs is the same person)
    engine.add_alldifferent([seats["x"], seats["y"], seats["z"]])
    engine.add_alldifferent([seats["american"], seats["english"], seats["french"]])
    cnf = engine.clausify()

    def right_to(a, b):
        """The seat a is immediately to the right of the seat b: for each seat of b, a is the next one."""
        for seat in range(3):
            cnf.append([-seats[b].equals(seat), seats[a].equals((seat + 1) % 3)])

    # the American sits to the right of Y, since Y passed to the American
    right_to("american", "y")
    # X sits to the right of the Frenchwoman, since X passed to the person who passed to her
    right_to("x", "french")

    return cnf, seats
