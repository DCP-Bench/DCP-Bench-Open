# Dudeney numbers: a number larger than 1, with at most n digits, that is a
# perfect cube whose digits add up to its cube root.
using JuMP

function build(instance)
    n = instance["n"]
    roots = 1:9 * n       # the digit sum is at most 9 * n
    model = Model()
    @variable(model, 0 <= digits[1:n] <= 9, Int)
    @variable(model, 2 <= number <= 10^n - 1, Int)
    # which cube root the number has
    @variable(model, root[roots], Bin)
    @constraint(model, sum(root) == 1)
    @constraint(model, number == sum(r^3 * root[r] for r in roots))
    # the digits add up to the cube root and spell the number
    @constraint(model, sum(digits) == sum(r * root[r] for r in roots))
    @constraint(model, number == sum(10^(n - i) * digits[i] for i in 1:n))
    return model, Dict("number" => number)
end
