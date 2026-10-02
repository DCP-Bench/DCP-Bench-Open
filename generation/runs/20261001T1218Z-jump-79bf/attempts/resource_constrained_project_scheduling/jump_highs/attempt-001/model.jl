# Resource-constrained project scheduling: schedule jobs with given durations so that
# precedence constraints hold and, at every time, the jobs in progress do not use more of
# any renewable resource than its capacity. Minimise the makespan (the latest start time;
# the last job is a dummy of duration 0 that follows everything).
using JuMP

# A feasible schedule built greedily, used only to bound the time horizon: jobs are taken
# in an order that respects the precedences, and each starts at the earliest time at
# which its predecessors are done and the resources suffice. Returns the latest start.
function greedy_makespan(dur, need, cap, preds, order)
    n = length(dur)
    use = zeros(Int, length(cap), sum(dur) + maximum(dur) + 2)   # resource use at each time
    start = zeros(Int, n)
    for j in order
        t = maximum((start[p] + dur[p] for p in preds[j]); init = 0)
        while any(use[r, tau+1] + need[j][r] > cap[r] for r in eachindex(cap) for tau in t:t+dur[j]-1)
            t += 1
        end
        for r in eachindex(cap), tau in t:t+dur[j]-1
            use[r, tau+1] += need[j][r]
        end
        start[j] = t
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

    # Earliest start of each job: after its predecessors have finished (heads). Latest start
    # of each job: late enough that the longest chain of successors still starts by the
    # horizon (tails).
    horizon = greedy_makespan(dur, need, cap, preds, order)   # a feasible latest start, so an optimum is no later
    earliest = zeros(Int, n)
    for j in order, p in preds[j]
        earliest[j] = max(earliest[j], earliest[p] + dur[p])
    end
    tail = zeros(Int, n)
    for j in reverse(order), k in succs[j]
        tail[j] = max(tail[j], dur[j] + tail[k])
    end
    latest = horizon .- tail

    model = Model()

    # starts_at[j][t - earliest[j] + 1] = 1 when job j starts at time t, between its earliest
    # and latest start; every job starts exactly once. A time-indexed formulation is used
    # because its linear relaxation is far tighter than big-M disjunctions for resources.
    starts_at = [@variable(model, [earliest[j]:latest[j]], Bin) for j in 1:n]
    @constraint(model, [j = 1:n], sum(starts_at[j]) == 1)
    # started_by(j, t) = 1 when job j has started at time t or earlier
    started_by(j, t) = sum((starts_at[j][u] for u in earliest[j]:min(t, latest[j])); init = 0)

    # Precedence: job b can have started by time t only if its predecessor a was started
    # dur[a] earlier.
    for (a, b) in arcs, t in earliest[b+1]:latest[b+1]
        @constraint(model, started_by(b + 1, t) <= started_by(a + 1, t - dur[a+1]))
    end

    # Resource capacity: at each time, the jobs in progress (started within their duration
    # before, or at, that time) use at most the capacity of each resource.
    for r in 1:R, tau in 0:horizon+maximum(dur)
        running = [starts_at[j][u] * need[j][r] for j in 1:n if need[j][r] > 0 && dur[j] > 0
                   for u in max(earliest[j], tau - dur[j] + 1):min(latest[j], tau)]
        isempty(running) || @constraint(model, sum(running) <= cap[r])
    end

    # start_time[j] = the time job j starts (declared output)
    start_time = [sum(u * starts_at[j][u] for u in earliest[j]:latest[j]) for j in 1:n]

    # The makespan is the latest start time; minimise it
    @variable(model, 0 <= makespan <= horizon)
    @constraint(model, [j = 1:n], makespan >= start_time[j])
    @objective(model, Min, makespan)

    return model, Dict("start_time" => start_time)
end
