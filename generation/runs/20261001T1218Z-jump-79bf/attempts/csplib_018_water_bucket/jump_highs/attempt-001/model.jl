# Water bucket: three buckets with given capacities hold all the water in the initial
# state. Pouring one bucket into another until the source is empty or the target is full is
# a transfer. Reach the goal state with the fewest transfers, and print the sequence of
# states padded to a fixed length.
using JuMP

function build(instance)
    capacities = instance["capacities"]
    initial_state = instance["initial_state"]
    goal_state = instance["goal_state"]
    max_steps = instance["MAX_STEPS"]          # length of the printed sequence
    padding = instance["PADDING_VALUE"]        # value written in every bucket after the goal
    buckets = length(capacities)
    total_water = maximum(initial_state)       # water is conserved by pouring

    # All states the buckets can be in: (first, second, third) amounts within each capacity
    # that add up to the total water.
    states = [(i, j, total_water - i - j)
              for i in 0:capacities[1] for j in 0:capacities[2]
              if 0 <= total_water - i - j <= capacities[3]]
    state_index = Dict(s => k for (k, s) in enumerate(states))

    # Pouring bucket a into bucket b moves min(water in a, free room in b) and counts only when
    # it moves something. successors[k] lists the states one transfer away from state k.
    successors = [Int[] for _ in states]
    for (k, state) in enumerate(states), a in 1:buckets, b in 1:buckets
        a == b && continue
        poured = min(state[a], capacities[b] - state[b])
        if poured > 0
            after = collect(state)
            after[a] -= poured
            after[b] += poured
            push!(successors[k], state_index[Tuple(after)])
        end
    end
    start = state_index[Tuple(initial_state)]
    goal = state_index[Tuple(goal_state)]

    model = Model()

    # at[t, k] = 1 when step t of the sequence is state k; done[t] = 1 when step t is a padding
    # step, which is the case once the goal has been reached. Every step is one or the other.
    @variable(model, at[1:max_steps, 1:length(states)], Bin)
    @variable(model, done[1:max_steps], Bin)
    @constraint(model, [t = 1:max_steps], sum(at[t, :]) + done[t] == 1)

    # the sequence starts with the initial state
    @constraint(model, at[1, start] == 1)

    for t in 1:max_steps-1
        # a state that is not the goal is followed by a state one transfer away
        for k in 1:length(states)
            k == goal && continue
            @constraint(model, at[t, k] <= sum([at[t+1, s] for s in successors[k]]; init = 0))
        end
        # the goal is followed by padding, and padding by padding
        @constraint(model, done[t+1] >= at[t, goal])
        @constraint(model, done[t+1] >= done[t])
    end

    # the goal state must be reached
    @constraint(model, sum(at[:, goal]) >= 1)

    # cost = the number of transfers = the number of states before the padding starts, minus 1;
    # it has its own bounded variable so that enumeration cuts a single quantity
    @variable(model, 0 <= cost <= max_steps - 1, Int)
    @constraint(model, cost == sum(1 - done[t] for t in 1:max_steps) - 1)
    @objective(model, Min, cost)

    # sequence[t, b] = the amount in bucket b at step t, or the padding value after the goal
    @variable(model, min(padding, 0) <= sequence[1:max_steps, 1:buckets] <= total_water, Int)
    @constraint(model, [t = 1:max_steps, b = 1:buckets],
                sequence[t, b] == sum(states[k][b] * at[t, k] for k in 1:length(states)) +
                                  padding * done[t])

    return model, Dict("cost" => cost, "sequence" => sequence)
end
