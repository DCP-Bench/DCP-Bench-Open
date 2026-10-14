# Car sequencing: order the cars on an assembly line so that every option's
# station is never overloaded. Each car belongs to a type, each type needs some
# options, and for option o at most at_most[o] of any per_slots[o] consecutive
# cars may require it.
using JuMP

function build(instance)
    at_most = instance["at_most"]      # most cars needing option o in a window
    per_slots = instance["per_slots"]  # window length for option o
    demand = instance["demand"]        # number of cars of each type
    requires = instance["requires"]    # requires[t][o] = 1 if type t needs option o

    n_cars = sum(demand)               # one slot per car
    n_types = length(demand)
    n_options = length(at_most)

    model = Model()

    # is_type[s, t] = 1 when the car in slot s is of type t (types are 1-based here)
    @variable(model, is_type[1:n_cars, 1:n_types], Bin)
    # every slot holds exactly one car
    @constraint(model, [s = 1:n_cars], sum(is_type[s, :]) == 1)

    # the sequence of car types, 0-based as the problem declares; its bounds
    # come from the number of types
    @variable(model, 0 <= sequence[1:n_cars] <= n_types - 1, Int)
    @constraint(model, [s = 1:n_cars], sequence[s] == sum((t - 1) * is_type[s, t] for t in 1:n_types))

    # the number of cars of each type in the sequence equals its demand
    @constraint(model, [t = 1:n_types], sum(is_type[:, t]) == demand[t])

    # station capacity: among any per_slots[o] consecutive cars, at most
    # at_most[o] need option o (the options of slot s are the sum of the
    # requirement rows of the types it can hold)
    for o in 1:n_options, s in 1:(n_cars - per_slots[o] + 1)
        @constraint(model, sum(requires[t][o] * is_type[k, t]
                               for k in s:(s + per_slots[o] - 1), t in 1:n_types) <= at_most[o])
    end

    return model, Dict("sequence" => sequence)
end
