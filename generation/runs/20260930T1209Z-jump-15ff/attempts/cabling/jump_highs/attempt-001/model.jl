# Cabling: put the devices one above another in a rack, one device per slot, so
# that the total cable length is as small as possible. The cables between two
# devices cost their count times the distance between the two slots.
using JuMP

function build(instance)
    n = instance["n"]
    devices = instance["devices"]
    cables = instance["cable_struct"]    # [device a, device b, number of cables]
    index = Dict(name => i for (i, name) in enumerate(devices))
    model = Model()
    @variable(model, at[1:n, 1:n], Bin)   # device d in slot p
    @constraint(model, [d = 1:n], sum(at[d, :]) == 1)
    @constraint(model, [p = 1:n], sum(at[:, p]) == 1)
    @variable(model, 1 <= slot[1:n] <= n, Int)
    @constraint(model, [d = 1:n], slot[d] == sum(p * at[d, p] for p in 1:n))
    # the distance of each cable group, exact because it is minimised
    links = [(index[cable[1]], index[cable[2]], cable[3]) for cable in cables]
    @variable(model, 0 <= dist[1:length(links)] <= n - 1, Int)
    for (k, (a, b, _)) in enumerate(links)
        @constraint(model, dist[k] >= slot[a] - slot[b])
        @constraint(model, dist[k] >= slot[b] - slot[a])
    end
    @variable(model, 0 <= final_sum <= (n - 1) * sum(l[3] for l in links), Int)
    @constraint(model, final_sum == sum(links[k][3] * dist[k] for k in 1:length(links)))
    @objective(model, Min, final_sum)
    return model, Dict("final_sum" => final_sum)
end
