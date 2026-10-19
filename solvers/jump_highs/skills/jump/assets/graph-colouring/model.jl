# Graph colouring: fewest colours so that adjacent nodes differ (minimise the colours used).
using JuMP, HiGHS

n = 6
edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (5, 6)]   # a 5-cycle with a pendant node
K = n                                                      # at most n colours are ever needed

model = Model(HiGHS.Optimizer)
set_silent(model)
set_attribute(model, "mip_rel_gap", 0.0)                   # prove the optimum, not just a good value

@variable(model, x[1:n, 1:K], Bin)     # x[i, c] = 1 when node i has colour c
@variable(model, used[1:K], Bin)       # used[c] = 1 when colour c appears anywhere

for i in 1:n
    @constraint(model, sum(x[i, c] for c in 1:K) == 1)      # exactly one colour per node
end
for (i, j) in edges, c in 1:K
    @constraint(model, x[i, c] + x[j, c] <= 1)               # adjacent nodes differ
end
for i in 1:n, c in 1:K
    @constraint(model, x[i, c] <= used[c])                   # a colour in use is marked
end
@objective(model, Min, sum(used))

optimize!(model)
println("Status: ", termination_status(model))
colour = [findfirst(c -> round(Int, value(x[i, c])) == 1, 1:K) for i in 1:n]
println("Colours used: ", round(Int, objective_value(model)))
println("Proper: ", all(colour[i] != colour[j] for (i, j) in edges))
