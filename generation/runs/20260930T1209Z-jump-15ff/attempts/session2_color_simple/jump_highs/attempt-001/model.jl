# Map colouring: colour the countries 1, 2, ... so that neighbours differ, with
# the largest colour used as small as possible.
using JuMP

function build(instance)
    graph = instance["graph"]       # pairs of neighbouring countries, 1-based
    n = maximum(maximum.(graph))    # number of countries
    model = Model()
    # has[c, k] = 1 when country c gets colour k
    @variable(model, has[1:n, 1:n], Bin)
    @constraint(model, [c = 1:n], sum(has[c, :]) == 1)
    # neighbours never share a colour
    @constraint(model, [e in graph, k = 1:n], has[e[1], k] + has[e[2], k] <= 1)
    @variable(model, 1 <= colors[1:n] <= n, Int)
    @constraint(model, [c = 1:n], colors[c] == sum(k * has[c, k] for k in 1:n))
    # the largest colour, as small as possible
    @variable(model, 1 <= largest <= n, Int)
    @constraint(model, [c = 1:n], colors[c] <= largest)
    @objective(model, Min, largest)
    return model, Dict("colors" => colors)
end
