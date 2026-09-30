# Diet: how many of each food to buy so that calories, chocolate, sugar and fat
# reach their minimum requirements at the least cost.
using JuMP

function build(instance)
    n = instance["n"]
    price = instance["price"]      # cost of each food, in cents
    limits = instance["limits"]    # least calories, chocolate, sugar and fat
    # The nutrition of the four foods is fixed by the problem (chocolate cake,
    # chocolate ice cream, cola, pineapple cheesecake); the rows are calories,
    # chocolate, sugar and fat.
    nutrition = [[400, 200, 150, 500],
                 [3, 2, 0, 0],
                 [2, 2, 4, 4],
                 [2, 4, 1, 5]]
    model = Model()
    @variable(model, 0 <= x[1:n] <= 10000, Int)
    @constraint(model, [k = 1:4], sum(nutrition[k][i] * x[i] for i in 1:n) >= limits[k])
    # the cost, a declared output, 0..1000 as the reference bounds it
    @variable(model, 0 <= cost <= 1000, Int)
    @constraint(model, cost == sum(price[i] * x[i] for i in 1:n))
    @objective(model, Min, cost)
    return model, Dict("cost" => cost)
end
