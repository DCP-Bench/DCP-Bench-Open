# Contracting costs: six tradesmen are paid in pairs, and the payment to each
# pair is known. Find what each man charges.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    @variable(model, 1 <= c[1:6] <= 5300, Int)
    paper_hanger, painter, plumber, electrician, carpenter, mason = c
    @constraint(model, paper_hanger + painter == 1100)
    @constraint(model, painter + plumber == 1700)
    @constraint(model, plumber + electrician == 1100)
    @constraint(model, electrician + carpenter == 3300)
    @constraint(model, carpenter + mason == 5300)
    @constraint(model, mason + painter == 3200)
    return model, Dict("paper_hanger" => paper_hanger, "painter" => painter, "plumber" => plumber,
                       "electrician" => electrician, "carpenter" => carpenter, "mason" => mason)
end
