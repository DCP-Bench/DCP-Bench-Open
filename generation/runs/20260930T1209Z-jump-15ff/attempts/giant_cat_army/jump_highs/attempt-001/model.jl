# Giant cat army riddle: start from 0 and extend the list by adding 5, adding 7
# or taking a square root, so that all 24 numbers are different integers of at
# most 60, the list holds 2 and later 10, and it ends with 14.
using JuMP

function build(instance)
    # The riddle fixes these numbers; the instance carries no data.
    maxval, n = 60, 24
    moves = Float64[t[k] for t in [(v, w) for v in 0:maxval for w in 0:maxval
                                   if w == v + 5 || w == v + 7 || w * w == v], k in 1:2]
    model = Model()
    @variable(model, 0 <= x[1:n] <= maxval, Int)
    @constraint(model, x in MOI.AllDifferent(n))
    fix(x[1], 0; force = true)
    fix(x[n], 14; force = true)
    # each step adds 5, adds 7 or takes the square root
    @constraint(model, [i = 1:n-1], [x[i], x[i + 1]] in MOI.Table(moves))
    # 2 comes before 10: where2[i] = 1 marks the position of 2, where10 that of 10
    @variable(model, where2[1:n], Bin)
    @variable(model, where10[1:n], Bin)
    @constraint(model, sum(where2) == 1)
    @constraint(model, sum(where10) == 1)
    @constraint(model, [i = 1:n], where2[i] --> {x[i] == 2})
    @constraint(model, [i = 1:n], where10[i] --> {x[i] == 10})
    @constraint(model, sum(i * where2[i] for i in 1:n) + 1 <= sum(i * where10[i] for i in 1:n))
    return model, Dict("x" => x)
end
