# Eighteen-hole golf: lay out a course of 18 holes, each of length 3, 4 or 5, whose total
# length is 72.
using JuMP

function build(instance)
    # The course is fixed by the problem; the instance carries no data.
    num_holes = 18       # number of holes
    total_length = 72    # total length of the course
    shortest, longest = 3, 5   # a hole is 3, 4 or 5 long

    model = Model()

    # holes[i] = the length of hole i
    @variable(model, shortest <= holes[1:num_holes] <= longest, Int)

    # the lengths add up to the length of the course
    @constraint(model, sum(holes) == total_length)

    return model, Dict("holes" => holes)
end
