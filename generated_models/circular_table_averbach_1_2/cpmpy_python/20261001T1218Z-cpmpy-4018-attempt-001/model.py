# Hearts at a circular table (Averbach): three players X, Y, Z of nationalities American,
# English, French sit around a table, each passing three cards to the person on their right.
# Y passed three hearts to the American; X passed the queen of spades and two diamonds to the
# person who passed their cards to the Frenchwoman. Find who is who.
import cpmpy as cp


def build(instance):
    # The instance carries no data: the puzzle and its three seats are fixed by the problem.
    n = 3

    # Seats are numbered 0, 1, 2 around the table, and seat s + 1 is to the right of seat s
    # (seat 0 is to the right of seat 2).
    def right_of(a, b):
        # seat a is immediately to the right of seat b
        return a == (b + 1) % n

    # x, y, z = seat of player X, Y, Z
    players = cp.intvar(0, n - 1, shape=(n,), name="players")
    x, y, z = players

    # american, english, french = seat of the American, the Englishwoman, the Frenchwoman
    nationalities = cp.intvar(0, n - 1, shape=(n,), name="nationalities")
    american, english, french = nationalities

    model = cp.Model()

    # The three players sit in three different seats.
    model += cp.AllDifferent(players)

    # The three nationalities sit in three different seats.
    model += cp.AllDifferent(nationalities)

    # Y passed three hearts to the American: the American is on Y's right.
    model += right_of(american, y)

    # X passed to the person (on X's right) who passed to the Frenchwoman, so the Frenchwoman is
    # two seats to the right of X; at a table of three that puts X on the Frenchwoman's right.
    model += right_of(x, french)

    return model, {"x": x, "y": y, "z": z,
                   "american": american, "english": english, "french": french}
