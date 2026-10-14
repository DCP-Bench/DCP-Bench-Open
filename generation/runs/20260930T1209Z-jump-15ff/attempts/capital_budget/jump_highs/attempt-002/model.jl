# Capital budgeting: choose investments whose cash outflow fits the budget and
# whose total net present value is as large as possible.
using JuMP

function build(instance)
    budget = instance["budget"]
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    n = length(npv)
    model = Model()
    # x[i] = 1 when investment i is chosen
    @variable(model, x[1:n], Bin)
    # z = the total net present value, a declared output
    @variable(model, 0 <= z <= sum(npv), Int)
    # the chosen investments fit the budget
    @constraint(model, sum(cash_flow[i] * x[i] for i in 1:n) <= budget)
    @constraint(model, z == sum(npv[i] * x[i] for i in 1:n))
    @objective(model, Max, z)
    return model, Dict("x" => x, "z" => z)
end
