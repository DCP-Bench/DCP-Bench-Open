# Candies: give every child at least one candy, a child with a higher rating
# than a neighbour more candies than that neighbour, and as few candies as
# possible in total.
using JuMP

function build(instance)
    ratings = instance["ratings"]
    n = length(ratings)
    model = Model()
    @variable(model, 1 <= x[1:n] <= n, Int)
    @variable(model, 1 <= z <= n * n, Int)
    @constraint(model, z == sum(x))
    @constraint(model, z >= n)
    for i in 2:n
        if ratings[i - 1] > ratings[i]
            @constraint(model, x[i - 1] >= x[i] + 1)
        elseif ratings[i - 1] < ratings[i]
            @constraint(model, x[i - 1] + 1 <= x[i])
        end
    end
    @objective(model, Min, z)
    return model, Dict("z" => z, "x" => x)
end
