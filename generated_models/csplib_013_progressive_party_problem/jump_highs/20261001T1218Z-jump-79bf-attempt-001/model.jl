# Progressive party: some boats are hosts and stay put; every other boat's crew
# visits one host in each period. A host holds at most its capacity at a time,
# a guest crew never revisits a host, and two crews meet at most once. Minimise
# the number of host boats.
using JuMP

function build(instance)
    n = instance["n_boats"]
    periods = instance["n_periods"]
    capacity = instance["capacity"]    # capacity[h] = most people aboard boat h at a time
    crew_size = instance["crew_size"]  # crew_size[b] = people in the crew of boat b

    model = Model()

    # is_host[h] = 1 when boat h is a host
    @variable(model, is_host[1:n], Bin)
    # at[p, b, h] = 1 when in period p the crew of boat b is aboard boat h
    # (a host's own crew is aboard that host, so b == h is allowed)
    @variable(model, at[1:periods, 1:n, 1:n], Bin)

    # each crew is aboard exactly one boat in each period
    @constraint(model, [p = 1:periods, b = 1:n], sum(at[p, b, :]) == 1)

    # only a host can be visited; and a host's crew stays aboard its own boat
    # in every period (at[p, h, h] is 1 exactly for hosts)
    @constraint(model, [p = 1:periods, b = 1:n, h = 1:n], at[p, b, h] <= is_host[h])
    @constraint(model, [p = 1:periods, h = 1:n], at[p, h, h] >= is_host[h])

    # the number of people aboard a boat in a period never exceeds its capacity
    @constraint(model, [p = 1:periods, h = 1:n],
                sum(crew_size[b] * at[p, b, h] for b in 1:n) <= capacity[h])

    # a guest crew cannot visit the same host twice
    @constraint(model, [b = 1:n, h = 1:n; b != h], sum(at[p, b, h] for p in 1:periods) <= 1)

    # two crews cannot be aboard the same boat in more than one period;
    # meet[p, b1, b2] is forced to 1 when both crews are aboard one boat in period p
    for b1 in 1:n-1, b2 in b1+1:n
        meet = @variable(model, [1:periods], Bin)
        @constraint(model, [p = 1:periods, h = 1:n], meet[p] >= at[p, b1, h] + at[p, b2, h] - 1)
        @constraint(model, sum(meet) <= 1)
    end

    # visits[p, b] = the (0-based) boat visited by boat b in period p, a declared output
    @variable(model, 0 <= visits[1:periods, 1:n] <= n - 1, Int)
    @constraint(model, [p = 1:periods, b = 1:n],
                visits[p, b] == sum((h - 1) * at[p, b, h] for h in 1:n))

    # minimise the number of host boats
    @objective(model, Min, sum(is_host))
    return model, Dict("visits" => visits, "is_host" => is_host)
end
