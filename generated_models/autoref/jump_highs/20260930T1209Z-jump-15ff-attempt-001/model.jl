# Autoref: a series s[0..n+1] in which every value i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] is m.
using JuMP

function build(instance)
    n = instance["n"]
    m = instance["m"]
    len = n + 2
    model = Model()
    # is[k, v + 1] = 1 when element k (1-based) is v
    @variable(model, is[1:len, 1:n+1], Bin)
    @constraint(model, [k = 1:len], sum(is[k, :]) == 1)
    @variable(model, 0 <= s[1:len] <= n, Int)
    @constraint(model, [k = 1:len], s[k] == sum(v * is[k, v + 1] for v in 0:n))
    fix(s[len], m; force = true)
    # the value v occurs s[v] times
    @constraint(model, [v = 0:n], sum(is[:, v + 1]) == s[v + 1])
    return model, Dict("s" => s)
end
