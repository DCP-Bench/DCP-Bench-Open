# Who killed Agatha: Agatha, the butler and Charles live in Dreadsbury Mansion.
# A killer always hates, and is no richer than, his victim. Charles hates no one
# Agatha hates. Agatha hates everybody except the butler. The butler hates
# everyone not richer than Agatha, and everyone Agatha hates. No one hates
# everyone. The killer is a 0-based index into the names.
using JuMP

function build(instance)
    n = length(instance["names"])     # Agatha, the butler and Charles
    agatha, butler, charles = 1, 2, 3
    model = Model()
    @variable(model, hates[1:n, 1:n], Bin)
    @variable(model, richer[1:n, 1:n], Bin)
    # is_killer[k] = 1 when person k killed Agatha
    @variable(model, is_killer[1:n], Bin)
    @constraint(model, sum(is_killer) == 1)
    # a killer hates his victim and is no richer than her
    @constraint(model, [k = 1:n], is_killer[k] <= hates[k, agatha])
    @constraint(model, [k = 1:n], is_killer[k] <= 1 - richer[k, agatha])
    # no one is richer than himself, and of two people exactly one is the richer
    @constraint(model, [i = 1:n], richer[i, i] == 0)
    @constraint(model, [i = 1:n, j = i+1:n], richer[i, j] + richer[j, i] == 1)
    for i in 1:n
        # Charles hates no one that Agatha hates
        @constraint(model, hates[agatha, i] + hates[charles, i] <= 1)
        # the butler hates everyone not richer than Agatha, and everyone Agatha hates
        @constraint(model, hates[butler, i] >= 1 - richer[i, agatha])
        @constraint(model, hates[butler, i] >= hates[agatha, i])
        # no one hates everyone
        @constraint(model, sum(hates[i, :]) <= n - 1)
    end
    # Agatha hates everybody except the butler
    fix(hates[agatha, agatha], 1; force = true)
    fix(hates[agatha, charles], 1; force = true)
    fix(hates[agatha, butler], 0; force = true)
    @variable(model, 0 <= killer <= n - 1, Int)
    @constraint(model, killer == sum((k - 1) * is_killer[k] for k in 1:n))
    return model, Dict("killer" => killer)
end
