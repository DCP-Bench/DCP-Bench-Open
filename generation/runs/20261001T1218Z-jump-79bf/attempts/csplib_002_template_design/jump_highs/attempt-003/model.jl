# Template design: a print run uses templates, each holding n_slots slots that carry copies
# of the product variations. Choose the layout of each template (how many copies of each
# variation) and how many sheets are printed from each template, so that every variation's
# demand is met with as few printed sheets in total as possible.
using JuMP

# All ways to fill `slots` slots with copies of `parts` variations, at most `most` copies of
# each: the vectors of `parts` numbers in 0..most that add up to `slots`.
function layouts(slots, parts, most)
    parts == 0 && return slots == 0 ? [Int[]] : Vector{Int}[]
    found = Vector{Int}[]
    for copies in 0:min(slots, most)
        for rest in layouts(slots - copies, parts - 1, most)
            push!(found, vcat(copies, rest))
        end
    end
    return found
end

function build(instance)
    n_slots = instance["n_slots"]          # slots on one template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v] = items wanted of variation v

    ub = maximum(demand)                   # most sheets printed from one template (the reference's bound)

    # Every possible layout of one template: all slots populated, at most n_var copies of a
    # variation (the reference's bound on a count).
    options = layouts(n_slots, n_var, n_var)
    N = length(options)

    model = Model()

    # production[t] = number of sheets printed from template t (declared output)
    @variable(model, 1 <= production[1:n_templates] <= ub, Int)
    # layout[t, v] = copies of variation v on template t (declared output)
    @variable(model, 0 <= layout[1:n_templates, 1:n_var] <= n_var, Int)

    # picks[t, o] = 1 when template t has the o-th layout; each template has exactly one.
    @variable(model, picks[1:n_templates, 1:N], Bin)
    @constraint(model, [t = 1:n_templates], sum(picks[t, o] for o in 1:N) == 1)
    @constraint(model, [t = 1:n_templates, v = 1:n_var],
                layout[t, v] == sum(options[o][v] * picks[t, o] for o in 1:N))

    # sheets[t, o] = the sheets printed from template t if it has layout o, else 0. Picking
    # layouts first makes the demand constraint linear: the product of the sheets and
    # the number of copies on a template becomes (copies in the layout) * sheets[t, o].
    @variable(model, 0 <= sheets[1:n_templates, 1:N] <= ub)
    @constraint(model, [t = 1:n_templates, o = 1:N], sheets[t, o] <= ub * picks[t, o])
    @constraint(model, [t = 1:n_templates], production[t] == sum(sheets[t, o] for o in 1:N))

    # meet demand: the printed sheets carry at least demand[v] copies of variation v
    @constraint(model, [v = 1:n_var],
                sum(options[o][v] * sheets[t, o] for t in 1:n_templates, o in 1:N) >= demand[v])

    # implied: every template fills all its slots, so the sheets cover the total demand
    @constraint(model, n_slots * sum(production) >= sum(demand))

    # minimise the number of printed sheets
    @objective(model, Min, sum(production))

    return model, Dict("production" => production, "layout" => layout)
end
