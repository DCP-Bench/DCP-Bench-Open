# Car selection: assign participants to cars they are interested in, each
# participant to at most one car and each car to at most one participant, with
# as many assignments as possible.
using JuMP

function build(instance)
    possible = instance["possible_assignments"]   # 1 when participant i likes car j
    np = length(possible)
    nc = length(possible[1])
    model = Model()
    @variable(model, a[1:np, 1:nc], Bin)
    # only cars the participant is interested in
    @constraint(model, [i = 1:np, j = 1:nc], a[i, j] <= possible[i][j])
    # each participant gets at most one car, and each car at most one participant
    @constraint(model, [i = 1:np], sum(a[i, :]) <= 1)
    @constraint(model, [j = 1:nc], sum(a[:, j]) <= 1)
    @objective(model, Max, sum(a))
    return model, Dict("assignments" => a)
end
