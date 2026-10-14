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

    # Each pair of golfers meets in at most one week. together[w] = 1 is allowed to
    # stand for "g1 and g2 are in the same group in week w" and it is forced whenever
    # their group numbers are equal: if together[w] = 0 the two group numbers differ,
    # which is assign1 > assign2 (above[w] = 1) or assign2 > assign1 (above[w] = 0).
    # The big-M is n_groups, the largest possible difference plus one. This takes two
    # rows per pair and week where linking through the group indicators takes n_groups.
    for g1 in 1:n_golfers-1, g2 in g1+1:n_golfers
        together = @variable(model, [1:n_weeks], Bin)
        above = @variable(model, [1:n_weeks], Bin)
        @constraint(model, [w = 1:n_weeks],
                    assign[g1, w] - assign[g2, w] >= 1 - n_groups * (together[w] + 1 - above[w]))
        @constraint(model, [w = 1:n_weeks],
                    assign[g2, w] - assign[g1, w] >= 1 - n_groups * (together[w] + above[w]))
        @constraint(model, sum(together) <= 1)
    end

    return model, Dict("assign" => assign)
end
