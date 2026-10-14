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

    # each group has exactly group_size players in every week
    @constraint(model, [w = 1:n_weeks, k = 1:n_groups], sum(in_group[:, w, k]) == group_size)

    # Each pair of golfers meets in at most one week. together[w] is forced to 1 when
    # golfers g1 and g2 are both in the same group k in week w (it may be 1 otherwise,
    # which only makes the limit of one week stricter, so it needs no upper link).
    for g1 in 1:n_golfers-1, g2 in g1+1:n_golfers
        together = @variable(model, [1:n_weeks], Bin)
        @constraint(model, [w = 1:n_weeks, k = 1:n_groups],
                    together[w] >= in_group[g1, w, k] + in_group[g2, w, k] - 1)
        @constraint(model, sum(together) <= 1)
    end

    # assign[g, w] = the (0-based) group of golfer g in week w, a declared output. It is an
    # expression of the group indicators, so enumeration excludes earlier answers through
    # the indicators themselves.
    assign = [sum((k - 1) * in_group[g, w, k] for k in 1:n_groups) for g in 1:n_golfers, w in 1:n_weeks]

    return model, Dict("assign" => assign)
end
