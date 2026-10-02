# Resource-constrained project scheduling: schedule jobs with given durations so that
# precedence constraints hold and, at every time, the jobs in progress do not use more of
# any renewable resource than its capacity. Minimise the makespan (the latest start time;
# the last job is a dummy of duration 0 that follows everything).
using JuMP

# A feasible schedule built greedily, used only to bound the time horizon: jobs are taken
# one at a time among those whose predecessors are all placed, the one `choose` picks, and
# each starts at the earliest time at which its predecessors are done and the resources
# suffice. Returns the latest start time of the schedule.
function greedy_makespan(dur, need, cap, preds, choose)
    n = length(dur)
    use = zeros(Int, length(cap), sum(dur) + maximum(dur) + 2)   # resource use at each time
    start = zeros(Int, n)
    placed = Int[]
    while length(placed) < n
        ready = [j for j in 1:n if !(j in placed) && all(p in placed for p in preds[j])]
        j = choose(ready)
        t = maximum((start[p] + dur[p] for p in preds[j]); init = 0)
        while any(use[r, tau+1] + need[j][r] > cap[r] for r in eachindex(cap) for tau in t:t+dur[j]-1)
            t += 1
        end
        for r in eachindex(cap), tau in t:t+dur[j]-1
            use[r, tau+1] += need[j][r]
        end
        start[j] = t
        push!(placed, j)
    end
    return maximum(start)
end

function build(instance)
    dur = instance["durations_data"]                  # duration of each job
    need = instance["resource_needs_data"]            # need[j][r] = units of resource r job j uses
    cap = instance["resource_capacities_data"]        # capacity of each resource
    arcs = instance["successors_link_data"]           # [a, b] = job a must finish before job b starts (0-based)
    n = length(dur)
    R = length(cap)

    preds = [Int[] for _ in 1:n]
    succs = [Int[] for _ in 1:n]
    for (a, b) in arcs
        push!(preds[b+1], a + 1)
        push!(succs[a+1], b + 1)
    end

    # an order of the jobs in which every job comes after its predecessors
    order = Int[]
    while length(order) < n
        push!(order, first(j for j in 1:n if !(j in order) && all(p in order for p in preds[j])))
    end

    # tail[j] = the longest chain of durations that must pass between the start of job j and
    # the start of the last job that depends on it
    tail = zeros(Int, n)
    for j in reverse(order), k in succs[j]
        tail[j] = max(tail[j], dur[j] + tail[k])
    end

    # Time horizon: no later than the latest start of a feasible schedule, so an optimal
    # schedule fits. The better of two greedy schedules is used: jobs in numbering order, and
    # the job with the longest remaining chain first.
    horizon = min(greedy_makespan(dur, need, cap, preds, ready -> first(ready)),
                  greedy_makespan(dur, need, cap, preds, ready -> ready[argmax(tail[ready])]))

    # Earliest start of each job: after its predecessors have finished. Latest start: late
    # enough that the longest chain of successors still starts by the horizon.
    earliest = zeros(Int, n)
    for j in order, p in preds[j]
        earliest[j] = max(earliest[j], earliest[p] + dur[p])
    end
    latest = horizon .- tail

    model = Model()

    # begun[j][t] = 1 when job j has started at time t or earlier, for t between its earliest
    # and latest start (before the earliest start it has not started, from the latest start
    # on it has). This cumulative form is monotone in t, has a tight linear relaxation and
    # keeps the resource rows short.
    begun = [@variable(model, [earliest[j]:latest[j]-1], Bin) for j in 1:n]
    @constraint(model, [j = 1:n, t = earliest[j]+1:latest[j]-1], begun[j][t] >= begun[j][t-1])

    # add_begun!(expr, c, j, t) adds c * (1 if job j has started by time t, else 0) to expr
    function add_begun!(expr, c, j, t)
        if t >= latest[j]
            add_to_expression!(expr, c)
        elseif t >= earliest[j]
            add_to_expression!(expr, c, begun[j][t])
        end
        return expr
    end

    # Precedence: job b can have started by time t only if its predecessor a had started by
    # t - dur[a] (it must have finished by then).
    for (a, b) in arcs, t in earliest[b+1]:latest[b+1]-1
        expr = AffExpr(0.0)
        add_begun!(expr, 1, b + 1, t)
        add_begun!(expr, -1, a + 1, t - dur[a+1])
        @constraint(model, expr <= 0)
    end

    # Resource capacity: at each time tau, the jobs in progress are those that started in the
    # last dur[j] time units (started by tau, but not by tau - dur[j]); together they use at
    # most the capacity of each resource.
    for r in 1:R, tau in 0:horizon+maximum(dur)
        expr = AffExpr(0.0)
        for j in 1:n
            if need[j][r] > 0 && dur[j] > 0
                add_begun!(expr, need[j][r], j, tau)
                add_begun!(expr, -need[j][r], j, tau - dur[j])
            end
        end
        isempty(expr.terms) || @constraint(model, expr <= cap[r])
    end

    # start_time[j] = the time job j starts (declared output): the latest start minus the
    # number of times from the earliest start on at which it has already started. It is
    # a variable of its own so that excluding an already found schedule moves only these n
    # variables instead of all the begun[j][t].
    @variable(model, earliest[j] <= start_time[j = 1:n] <= latest[j], Int)
    @constraint(model, [j = 1:n], start_time[j] == latest[j] - sum(begun[j]))

    # The makespan is the latest start time; minimise it
    @variable(model, 0 <= makespan <= horizon)
    @constraint(model, [j = 1:n], makespan >= start_time[j])
    @objective(model, Min, makespan)

    return model, Dict("start_time" => start_time)
end
