# Perfect square placement: pack squares of given integer side lengths into a
# larger square of side `base` without overlap, with all sides parallel to the
# big square. The areas of the small squares add up to the area of the big
# square, so the packing has no spare room.
using JuMP

function build(instance)
    base = instance["base"]     # side of the large square
    sides = instance["sides"]   # side lengths of the small squares
    n = length(sides)

    model = Model()

    # px[s][p] = 1 when square s has its lower-left corner at x-coordinate p, and
    # py[s][p] likewise for y. A square must stay inside the big square, so its
    # corner is at most base - side (the range of p).
    px = [@variable(model, [0:base-sides[s]], Bin) for s in 1:n]
    py = [@variable(model, [0:base-sides[s]], Bin) for s in 1:n]
    @constraint(model, [s = 1:n], sum(px[s]) == 1)
    @constraint(model, [s = 1:n], sum(py[s]) == 1)

    # x_coords[s], y_coords[s] = coordinates of the lower-left corner, from 0 (declared outputs)
    @variable(model, 0 <= x_coords[s = 1:n] <= base - sides[s], Int)
    @variable(model, 0 <= y_coords[s = 1:n] <= base - sides[s], Int)
    @constraint(model, [s = 1:n], x_coords[s] == sum(p * px[s][p] for p in 0:base-sides[s]))
    @constraint(model, [s = 1:n], y_coords[s] == sum(p * py[s][p] for p in 0:base-sides[s]))

    # No overlap: for every two squares a and b, one lies completely left of, right of,
    # below or above the other. sel[k] selects which of the four holds (a big-M with
    # M = base, the largest possible gap, switches the other three off).
    for a in 1:n-1, b in a+1:n
        sel = @variable(model, [1:4], Bin)
        @constraint(model, x_coords[a] + sides[a] <= x_coords[b] + base * (1 - sel[1]))  # a left of b
        @constraint(model, x_coords[b] + sides[b] <= x_coords[a] + base * (1 - sel[2]))  # b left of a
        @constraint(model, y_coords[a] + sides[a] <= y_coords[b] + base * (1 - sel[3]))  # a below b
        @constraint(model, y_coords[b] + sides[b] <= y_coords[a] + base * (1 - sel[4]))  # b below a
        @constraint(model, sum(sel) >= 1)
    end

    # Implied by the area equality and the non-overlap: every column and every row of
    # the big square is covered exactly once, so the squares crossing a column (or
    # row) have sides adding up to base. Square s crosses column c when its corner is
    # in c - side + 1 .. c. These constraints only strengthen the linear relaxation.
    for c in 0:base-1
        @constraint(model, sum(sides[s] * px[s][p] for s in 1:n
                               for p in max(0, c - sides[s] + 1):min(c, base - sides[s])) == base)
        @constraint(model, sum(sides[s] * py[s][p] for s in 1:n
                               for p in max(0, c - sides[s] + 1):min(c, base - sides[s])) == base)
    end

    return model, Dict("x_coords" => x_coords, "y_coords" => y_coords)
end
