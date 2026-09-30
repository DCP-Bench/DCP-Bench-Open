# Fixed charge: produce shirts, shorts and pants within the labour and cloth
# available; a product can only be made on its rented machine. Maximise the
# profit less the renting costs.
using JuMP

function build(instance)
    renting_cost = instance["renting_cost"]
    capacity = instance["capacity"]            # labour and cloth available
    max_production = instance["max_production"]
    product = instance["product"]              # [profit, machine (0-based)] per product
    use = instance["use"]                      # [labour, cloth] per unit of a product
    nm = length(renting_cost)
    np = length(product)
    nr = length(capacity)
    model = Model()
    @variable(model, rent[1:nm], Bin)
    @variable(model, 0 <= produce[1:np] <= max_production, Int)
    # the resources suffice
    @constraint(model, [r = 1:nr], sum(use[p][r] * produce[p] for p in 1:np) <= capacity[r])
    # a product is made only when its machine is rented
    @constraint(model, [p = 1:np], produce[p] <= max_production * rent[product[p][2] + 1])
    # z = profit less renting costs, 0..10000 as the reference bounds it
    @variable(model, 0 <= z <= 10000, Int)
    @constraint(model, z == sum(product[p][1] * produce[p] for p in 1:np) -
                           sum(renting_cost[m] * rent[m] for m in 1:nm))
    @objective(model, Max, z)
    return model, Dict("z" => z)
end
