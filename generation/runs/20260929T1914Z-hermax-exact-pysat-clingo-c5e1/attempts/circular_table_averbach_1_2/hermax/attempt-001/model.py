# Averbach's card-passing riddle: three players X, Y, Z of three different
# nationalities (American, English, French) sit round a table, each passing
# three cards to the person on their right. Y passed to the American, and X
# passed to the person who passed to the Frenchwoman. Find who is who.
# A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
from hermax.model import Model


def build(instance):
    # The riddle fixes everything; the instance carries no data.
    m = Model()

    # seats of the three players, all different
    x, y, z = (m.int(name, 0, 2) for name in "xyz")
    m &= m.vector([x, y, z]).all_different()

    # seats of the three nationalities, all different: the same seat number in
    # the player and nationality outputs denotes the same person
    american, english, french = (m.int(name, 0, 2) for name in ("american", "english", "french"))
    m &= m.vector([american, english, french]).all_different()

    def right_to(a, b):
        """The seat a is immediately to the right of the seat b: for each seat of b, a is the next one."""
        nonlocal m
        for seat in range(3):
            m &= (~(b == seat) | (a == (seat + 1) % 3))

    # the American sits to the right of Y, since Y passed to the American
    right_to(american, y)
    # X sits to the right of the Frenchwoman, since X passed to the person who passed to her
    right_to(x, french)

    return m, {"x": x, "y": y, "z": z, "american": american, "english": english, "french": french}
