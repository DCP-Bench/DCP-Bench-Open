# Schur's lemma: put n balls labelled 1..n into c boxes so that for any triple of balls
# x + y = z, the three are not all in the same box.
using JuMP

function build(instance)
    n = instance["n"]   # number of balls
    c = instance["c"]   # number of boxes

    model = Model()

    # in_box[i, j] = 1 when ball i is in box j; a ball is in exactly one box
    @variable(model, in_box[1:n, 1:c], Bin)
    @constraint(model, [i = 1:n], sum(in_box[i, j] for j in 1:c) == 1)

    # Not all of x, y, z = x + y share a box. For distinct x and y, at most two of the three
    # balls may be in box j. When x = y (z = 2x) the triple is the two balls x and z, and
    # they may not share a box.
    for x in 1:n-1, y in x:n-x
        z = x + y
        for j in 1:c
            if x == y
                @constraint(model, in_box[x, j] + in_box[z, j] <= 1)
            else
                @constraint(model, in_box[x, j] + in_box[y, j] + in_box[z, j] <= 2)
            end
        end
    end

    # balls[i] = the box (1..c) of ball i (declared output), read off the box indicators
    balls = [sum(j * in_box[i, j] for j in 1:c) for i in 1:n]
    return model, Dict("balls" => balls)
end
