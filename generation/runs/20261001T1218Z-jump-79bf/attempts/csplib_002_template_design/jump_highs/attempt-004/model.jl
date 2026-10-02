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
    bits = ndigits(ub, base = 2)           # binary digits needed to write a number up to ub

    model = Model()

    # production[t] = number of sheets printed from template t (declared output)
    @variable(model, 1 <= production[1:n_templates] <= ub, Int)

    # layout[t, v] = copies of variation v on template t (declared output); at most n_var
    # copies of a variation (the reference's bound)
    @variable(model, 0 <= layout[1:n_templates, 1:n_var] <= n_var, Int)

    # all slots are populated in each template
    @constraint(model, [t = 1:n_templates], sum(layout[t, v] for v in 1:n_var) == n_slots)

    # The demand constraint multiplies production[t] by layout[t, v], which is not linear.
    # Write the number of sheets in binary, production[t] = sum of 2^b * digit[t, b], so that
    # the product becomes a sum of 2^b * (digit * layout), and a binary times a small integer
    # (0..n_var) needs only a small big-M. copies[t, v, b] stands for digit[t, b] * layout[t, v].
    @variable(model, digit[1:n_templates, 0:bits-1], Bin)
    @constraint(model, [t = 1:n_templates], production[t] == sum(2^b * digit[t, b] for b in 0:bits-1))
    @variable(model, 0 <= copies[1:n_templates, 1:n_var, 0:bits-1] <= n_var)
    @constraint(model, [t = 1:n_templates, v = 1:n_var, b = 0:bits-1], copies[t, v, b] <= layout[t, v])
    @constraint(model, [t = 1:n_templates, v = 1:n_var, b = 0:bits-1], copies[t, v, b] <= n_var * digit[t, b])
    # Every template fills all its slots, so for each digit the copies over all variations
    # add up to n_slots when the digit is set. With the upper bounds above this makes
    # copies exactly digit * layout, and it keeps the relaxation tight.
    @constraint(model, [t = 1:n_templates, b = 0:bits-1],
                sum(copies[t, v, b] for v in 1:n_var) == n_slots * digit[t, b])

    # Meet demand: the sheets of all templates carry at least demand[v] copies of variation v
    @constraint(model, [v = 1:n_var],
                sum(2^b * copies[t, v, b] for t in 1:n_templates, b in 0:bits-1) >= demand[v])

    # implied: every template fills all its slots, so the sheets cover the total demand
    @constraint(model, n_slots * sum(production) >= sum(demand))

    # minimise the number of printed sheets
    @objective(model, Min, sum(production))

    return model, Dict("production" => production, "layout" => layout)
end
