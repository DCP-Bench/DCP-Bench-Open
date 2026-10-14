# SONET ring design: nodes communicate over rings; installing a node on a ring costs one
# add-drop multiplexer (ADM). Two nodes with traffic between them must share at least one
# ring, each ring hosts a limited number of nodes. Minimise the total number of ADMs.
using JuMP

function build(instance)
    r = instance["r"]                        # number of rings available
    n = instance["n"]                        # number of nodes
    demand = instance["demand"]              # demand[i][j] = traffic between nodes i and j
    capacity_nodes = instance["capacity_nodes"]   # most nodes ring k can accommodate

    model = Model()

    # ring_config[k, i] = 1 when node i is installed on ring k (declared output)
    @variable(model, ring_config[1:r, 1:n], Bin)

    # Demand satisfaction: nodes i and j with traffic between them share a ring. on_ring[k]
    # = 1 only if both are on ring k (it needs just the upper bounds, since at least one
    # of them must be 1), and at least one ring must carry both.
    for i in 1:n-1, j in i+1:n
        if demand[i][j] > 0
            on_ring = @variable(model, [1:r], Bin)
            @constraint(model, [k = 1:r], on_ring[k] <= ring_config[k, i])
            @constraint(model, [k = 1:r], on_ring[k] <= ring_config[k, j])
            @constraint(model, sum(on_ring) >= 1)
        end
    end

    # Ring capacity: ring k accommodates at most capacity_nodes[k] nodes
    @constraint(model, [k = 1:r], sum(ring_config[k, i] for i in 1:n) <= capacity_nodes[k])

    # total_adms = one ADM per node installed on a ring (declared output, its own variable
    # bounded by the number of node-ring pairs)
    @variable(model, 0 <= total_adms <= r * n, Int)
    @constraint(model, total_adms == sum(ring_config))

    # Minimise the total number of ADMs
    @objective(model, Min, total_adms)

    return model, Dict("ring_config" => ring_config, "total_adms" => total_adms)
end
