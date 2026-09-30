# Divisible by 1 through 9: a 10-digit number using each digit 0-9 once whose
# first n digits form a number divisible by n, for n = 1 to 10.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 10
    model = Model()
    @variable(model, 0 <= x[1:n] <= 9, Int)
    @constraint(model, x in MOI.AllDifferent(n))
    # t[i] = the number formed by the first i digits, and t[i] = i * k[i]
    @variable(model, 0 <= t[i = 1:n] <= 10^i - 1, Int)
    @variable(model, 0 <= k[i = 1:n] <= div(10^i - 1, i), Int)
    @constraint(model, t[1] == x[1])
    @constraint(model, [i = 2:n], t[i] == 10 * t[i - 1] + x[i])
    @constraint(model, [i = 1:n], t[i] == i * k[i])
    return model, Dict("number" => t[n])
end
