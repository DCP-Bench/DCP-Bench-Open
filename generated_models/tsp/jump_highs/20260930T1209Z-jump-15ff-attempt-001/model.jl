# Travelling salesman: the shortest round trip through all the cities, with the
# distance between two cities their Euclidean distance rounded to an integer.
using JuMP

function build(instance)
    locations = instance["locations"]
    n = length(locations)
    dist = [round(Int, hypot(p[1] - q[1], p[2] - q[2])) for p in locations, q in locations]
    model = Model()
    # arc[i, j] = 1 when the tour goes from city i to city j
    @variable(model, arc[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], arc[i, i] == 0)
    @constraint(model, [i = 1:n], sum(arc[i, :]) == 1)
    @constraint(model, [j = 1:n], sum(arc[:, j]) == 1)
    # no subtours (Miller-Tucker-Zemlin): order[i] is the position of city i after city 1
    @variable(model, 1 <= order[1:n] <= n, Int)
    fix(order[1], 1; force = true)
    @constraint(model, [i = 2:n, j = 2:n; i != j], order[i] - order[j] + n * arc[i, j] <= n - 1)
    @variable(model, 0 <= travel_distance <= sum(maximum(dist; dims = 2)), Int)
    @constraint(model, travel_distance == sum(dist[i, j] * arc[i, j] for i in 1:n, j in 1:n))
    @objective(model, Min, travel_distance)
    return model, Dict("travel_distance" => travel_distance)
end
