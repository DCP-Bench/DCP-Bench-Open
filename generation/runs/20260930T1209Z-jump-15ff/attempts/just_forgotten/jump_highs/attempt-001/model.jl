# Just forgotten: Joe's account number uses each digit 0 to n-1 once. In each of
# several tried sequences exactly a given number of digits are in their place.
using JuMP

function build(instance)
    sets = instance["sets"]
    correct = instance["num_correct_digits"]
    n = length(sets[1])
    model = Model()
    # at[i, d] = 1 when position i holds the digit d - 1
    @variable(model, at[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], sum(at[i, :]) == 1)
    @constraint(model, [d = 1:n], sum(at[:, d]) == 1)
    # every tried sequence has exactly num_correct digits in place
    @constraint(model, [tried in sets], sum(at[i, tried[i] + 1] for i in 1:n) == correct)
    @variable(model, 0 <= x[1:n] <= n - 1, Int)
    @constraint(model, [i = 1:n], x[i] == sum((d - 1) * at[i, d] for d in 1:n))
    return model, Dict("x" => x)
end
