# Social golfers: n_groups * group_size golfers play golf once a week in
# n_groups groups of group_size players, for n_weeks weeks, so that no two
# golfers are in the same group in more than one week.
using JuMP

function build(instance)
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    model = Model()

    # in_group[g, w, k] = 1 when golfer g plays in group k in week w
    @variable(model, in_group[1:n_golfers, 1:n_weeks, 1:n_groups], Bin)
    # every golfer plays in exactly one group each week
    @constraint(model, [g = 1:n_golfers, w = 1:n_weeks], sum(in_group[g, w, :]) == 1)

    # assign[g, w] = the (0-based) group of golfer g in week w, a declared output
    @variable(model, 0 <= assign[1:n_golfers, 1:n_weeks] <= n_groups - 1, Int)
    @constraint(model, [g = 1:n_golfers, w = 1:n_weeks],
                assign[g, w] == sum((k - 1) * in_group[g, w, k] for k in 1:n_groups))

    # each group has exactly group_size players in every week
    @constraint(model, [w = 1:n_weeks, k = 1:n_groups], sum(in_group[:, w, k]) == group_size)

    # each pair of golfers meets in at most one week.
    # together[w] = 1 exactly when golfers g1 and g2 share a group in week w:
    # it is forced up when both are in group k, and forced down when they are in different groups.
    pair_together = Dict{Tuple{Int,Int},Any}()   # together[w] vector of each pair
    for g1 in 1:n_golfers-1, g2 in g1+1:n_golfers
        together = @variable(model, [1:n_weeks], Bin)
        @constraint(model, [w = 1:n_weeks, k = 1:n_groups],
                    together[w] >= in_group[g1, w, k] + in_group[g2, w, k] - 1)
        @constraint(model, [w = 1:n_weeks, k = 1:n_groups],
                    together[w] <= 1 - in_group[g1, w, k] + in_group[g2, w, k])
        @constraint(model, sum(together) <= 1)
        pair_together[(g1, g2)] = together
    end

    # implied by the two constraints above: a golfer meets exactly group_size - 1
    # others in a week (this tightens the linear relaxation)
    @constraint(model, [g = 1:n_golfers, w = 1:n_weeks],
                sum(pair_together[(min(g, h), max(g, h))][w] for h in 1:n_golfers if h != g) == group_size - 1)

    return model, Dict("assign" => assign)
end
