# Appointment scheduling: give each of n people one of n interview slots, each
# slot to one person, so that every person gets a slot in which they are free.
using JuMP

function build(instance)
    m = instance["m"]   # m[i][j] = 1 when person i is free in slot j
    n = length(m)
    model = Model()

    # x[i, j] = 1 when person i is assigned to slot j
    @variable(model, x[1:n, 1:n], Bin)

    # each person gets exactly one slot
    @constraint(model, [i = 1:n], sum(x[i, :]) == 1)
    # each slot goes to exactly one person
    @constraint(model, [j = 1:n], sum(x[:, j]) == 1)
    # the slot a person gets must be one in which they are free
    @constraint(model, [i = 1:n], sum(m[i][j] * x[i, j] for j in 1:n) == 1)

    return model, Dict("x" => x)
end
