# N-queens with the diagonals written as all-different expressions (no auxiliary variables).
using JuMP, HiGHS

n = 8
model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, 0 <= q[1:n] <= n - 1, Int)                    # column of the queen in row i
@constraint(model, q in MOI.AllDifferent(n))                    # one queen per column
@constraint(model, [q[i] + i for i in 1:n] in MOI.AllDifferent(n))   # distinct up-diagonals
@constraint(model, [q[i] - i for i in 1:n] in MOI.AllDifferent(n))   # distinct down-diagonals

optimize!(model)
println("Status: ", termination_status(model))
if has_values(model)
    cols = [round(Int, value(q[i])) for i in 1:n]
    println("Queens: [", join(cols, ", "), "]")
    println("Valid: ", allunique(cols) && allunique(cols[i] + i for i in 1:n) && allunique(cols[i] - i for i in 1:n))
end
