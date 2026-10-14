# Hadamard matrix via Legendre pairs: for an odd l, two sequences a and b of l
# entries, each +1 or -1 and adding up to 1, whose periodic autocorrelations
# satisfy PAF(a, s) + PAF(b, s) = -2 for s = 1..(l-1)/2.
using JuMP

function build(instance)
    l = instance["l"]
    m = div(l - 1, 2)
    model = Model()
    # plus[q, i] = 1 when entry i of sequence q (a or b) is +1
    @variable(model, plus[1:2, 1:l], Bin)
    # the entries add up to 1: (l + 1) / 2 of them are +1
    @constraint(model, [q = 1:2], sum(plus[q, :]) == div(l + 1, 2))
    # PAF(q, s) = l - 2 * (entries i with entry i + s different), so the condition
    # is that the differing pairs of a and b together number l + 1
    for s in 1:m
        differ = @variable(model, [1:2, 1:l], Bin)
        for q in 1:2, i in 1:l
            j = mod1(i + s, l)
            # differ = plus[q, i] xor plus[q, j]
            @constraint(model, differ[q, i] >= plus[q, i] - plus[q, j])
            @constraint(model, differ[q, i] >= plus[q, j] - plus[q, i])
            @constraint(model, differ[q, i] <= plus[q, i] + plus[q, j])
            @constraint(model, differ[q, i] <= 2 - plus[q, i] - plus[q, j])
        end
        @constraint(model, sum(differ) == l + 1)
    end
    @variable(model, -1 <= a[1:l] <= 1, Int)
    @variable(model, -1 <= b[1:l] <= 1, Int)
    @constraint(model, [i = 1:l], a[i] == 2 * plus[1, i] - 1)
    @constraint(model, [i = 1:l], b[i] == 2 * plus[2, i] - 1)
    return model, Dict("a" => a, "b" => b)
end
