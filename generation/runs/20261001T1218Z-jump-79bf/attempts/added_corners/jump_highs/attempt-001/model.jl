# Added corners: write the digits 1 through 8 in the circles and squares of a 3 by 3 frame
# so that the number in each square is the sum of the two circles next to it.
#
#   C F C        positions are read like a book: a b c / d e / f g h
#   F   F        (a, c, f, h are the circles at the corners,
#   C F C         b, d, e, g are the squares between them)
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 8   # number of digits and of positions

    model = Model()

    # positions[1..8] = a, b, c, d, e, f, g, h, each a digit from 1 to n
    @variable(model, 1 <= positions[1:n] <= n, Int)
    a, b, c, d, e, f, g, h = positions

    # every digit is used once
    @constraint(model, positions in MOI.AllDifferent(n))

    # each square holds the sum of the two circles adjoining it
    @constraint(model, b == a + c)   # top square
    @constraint(model, d == a + f)   # left square
    @constraint(model, e == c + h)   # right square
    @constraint(model, g == f + h)   # bottom square

    return model, Dict("positions" => positions)
end
