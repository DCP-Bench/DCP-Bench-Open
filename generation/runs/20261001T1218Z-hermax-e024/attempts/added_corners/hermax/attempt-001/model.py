# Added corners: put the digits 1 through 8 in the eight places of a 3 by 3 square
# without its centre, so that each of the four side places (squares) holds the sum of the
# two corner places (circles) next to it. Places are numbered like reading a book:
#   a b c
#   d   e
#   f g h
from hermax.model import Model


def build(instance):
    # This puzzle has no instance data: the eight digits and the shape of the square are
    # part of the problem itself, so they are written here as constants.
    n = 8  # the digits 1..n
    m = Model()
    # positions[0..7] = the values of a, b, c, d, e, f, g, h in that order
    positions = m.int_vector("positions", n, 1, n)
    a, b, c, d, e, f, g, h = (positions[i] for i in range(n))

    # each digit is used once
    m &= positions.all_different()
    # the side place b is the sum of the corners a and c next to it
    m &= (b == a + c)
    # the side place d is the sum of the corners a and f next to it
    m &= (d == a + f)
    # the side place e is the sum of the corners c and h next to it
    m &= (e == c + h)
    # the side place g is the sum of the corners f and h next to it
    m &= (g == f + h)

    return m, {"positions": positions}
