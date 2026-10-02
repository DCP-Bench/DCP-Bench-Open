# Template design: a print run uses templates, each holding n_slots slots that carry copies
# of the product variations. Choose the layout of each template (how many copies of each
# variation) and how many sheets are printed from each template, so that every variation's
# demand is met with as few printed sheets in total as possible.
using JuMP

function build(instance)
    n_slots = instance["n_slots"]          # slots on one template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v] = items wanted of variation v

    ub = maximum(demand)                   # most sheets printed from one template (the reference's bound)

    model = Model()

    # production[t] = number of sheets printed from template t (declared output)
    @variable(model, 1 <= production[1:n_templates] <= ub, Int)

    # has[t, v, k] = 1 when template t carries k copies of variation v (k up to n_var, the
    # reference's bound); each variation has one count on each template.
    @variable(model, has[1:n_templates, 1:n_var, 0:n_var], Bin)
    @constraint(model, [t = 1:n_templates, v = 1:n_var], sum(has[t, v, k] for k in 0:n_var) == 1)

    # layout[t][v] = copies of variation v on template t (declared output)
    layout = [sum(k * has[t, v, k] for k in 0:n_var) for t in 1:n_templates, v in 1:n_var]

    # all slots are populated in each template
    @constraint(model, [t = 1:n_templates], sum(layout[t, v] for v in 1:n_var) == n_slots)

    # Meet demand: the sheets of all templates carry at least demand[v] copies of v, i.e.
    # sum over templates of production[t] * layout[t][v] >= demand[v]. The product of two
    # variables is not linear, so printed[t, v, k] stands for production[t] when the template
    # has k copies and is capped by production[t] and by ub * has[t, v, k] (an upper
    # bound is enough, since the copies only have to reach the demand).
    @variable(model, 0 <= printed[1:n_templates, 1:n_var, 0:n_var] <= ub)
    @constraint(model, [t = 1:n_templates, v = 1:n_var, k = 0:n_var], printed[t, v, k] <= production[t])
    @constraint(model, [t = 1:n_templates, v = 1:n_var, k = 0:n_var], printed[t, v, k] <= ub * has[t, v, k])
    @constraint(model, [v = 1:n_var],
                sum(k * printed[t, v, k] for t in 1:n_templates, k in 0:n_var) >= demand[v])

    # implied: every template fills all its slots, so the sheets cover the total demand
    @constraint(model, n_slots * sum(production) >= sum(demand))

    # minimise the number of printed sheets
    @objective(model, Min, sum(production))

    return model, Dict("production" => production, "layout" => layout)
end
