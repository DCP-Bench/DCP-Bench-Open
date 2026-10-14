# Perfect square placement: pack squares of given integer side lengths into a
# larger square of side `base` without overlap, with all sides parallel to the
# big square. The areas of the small squares add up to the area of the big
# square, so the packing has no spare room.
using JuMP

# Post "square a lies completely before square b along one axis" (a's far edge is
# at or before b's near edge) when `before` is 1. cum_a[t] = 1 when a's corner is at
# coordinate t or lower, likewise cum_b. The edges are in order exactly when, for every
# t, "b's corner is at most t" implies "a's corner is at most t - side_a". Each of these
# implications is a linear constraint with a coefficient of only 1 on `before`, which is
# a much tighter relaxation than a big-M constraint on the coordinates.
function post_before!(model, cum_a, side_a, cum_b, side_b, base, before)
    for t in 0:base-side_b
        if t - side_a < 0
            @constraint(model, cum_b[t] <= 1 - before)   # no room before b's corner at t
        else
            @constraint(model, cum_b[t] <= cum_a[t - side_a] + 1 - before)
        end
    end
end

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

    # cumx[s][t] = 1 when the corner of square s is at x-coordinate t or lower (a running
    # sum of px[s]); cumy likewise for y.
    cumx = [@variable(model, [0:base-sides[s]], lower_bound = 0, upper_bound = 1) for s in 1:n]
    cumy = [@variable(model, [0:base-sides[s]], lower_bound = 0, upper_bound = 1) for s in 1:n]
    for s in 1:n
        @constraint(model, cumx[s][0] == px[s][0])
        @constraint(model, cumy[s][0] == py[s][0])
        @constraint(model, [t = 1:base-sides[s]], cumx[s][t] == cumx[s][t-1] + px[s][t])
        @constraint(model, [t = 1:base-sides[s]], cumy[s][t] == cumy[s][t-1] + py[s][t])
    end

    # x_coords[s], y_coords[s] = coordinates of the lower-left corner, from 0 (declared outputs)
    @variable(model, 0 <= x_coords[s = 1:n] <= base - sides[s], Int)
    @variable(model, 0 <= y_coords[s = 1:n] <= base - sides[s], Int)
    @constraint(model, [s = 1:n], x_coords[s] == sum(p * px[s][p] for p in 0:base-sides[s]))
    @constraint(model, [s = 1:n], y_coords[s] == sum(p * py[s][p] for p in 0:base-sides[s]))

    # No overlap: for every two squares a and b, one lies completely left of, right of,
    # below or above the other. sel[k] selects which of the four holds.
    for a in 1:n-1, b in a+1:n
        sel = @variable(model, [1:4], Bin)
        post_before!(model, cumx[a], sides[a], cumx[b], sides[b], base, sel[1])  # a left of b
        post_before!(model, cumx[b], sides[b], cumx[a], sides[a], base, sel[2])  # b left of a
        post_before!(model, cumy[a], sides[a], cumy[b], sides[b], base, sel[3])  # a below b
        post_before!(model, cumy[b], sides[b], cumy[a], sides[a], base, sel[4])  # b below a
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
