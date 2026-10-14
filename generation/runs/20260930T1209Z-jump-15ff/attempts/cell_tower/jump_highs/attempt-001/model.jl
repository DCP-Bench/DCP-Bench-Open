# Cell towers: choose sites to build towers on within the budget so that the
# population of the regions they cover is as large as possible.
using JuMP

function build(instance)
    delta = instance["delta"]           # delta[i][j] = 1 when site i covers region j
    cost = instance["cost"]
    population = instance["population"]
    budget = instance["budget"]
    ns = length(cost)
    nr = length(population)
    model = Model()
    @variable(model, build_tower[1:ns], Bin)
    @variable(model, covered[1:nr], Bin)
    # a region counts as covered only if a tower covering it is built
    @constraint(model, [j = 1:nr], covered[j] <= sum(delta[i][j] * build_tower[i] for i in 1:ns))
    # the towers fit the budget
    @constraint(model, sum(cost[i] * build_tower[i] for i in 1:ns) <= budget)
    # the population covered, a declared output
    @variable(model, 0 <= total <= sum(population), Int)
    @constraint(model, total == sum(population[j] * covered[j] for j in 1:nr))
    @objective(model, Max, total)
    return model, Dict("build_tower" => build_tower, "total_population_covered" => total)
end
