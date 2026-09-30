# SEND + MORE = MONEY: give each letter a different digit, with no leading zero
# in SEND, MORE or MONEY, so that the addition is correct.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    @variable(model, 0 <= d[1:8] <= 9, Int)
    s, e, n, dd, m, o, r, y = d
    # every letter stands for a different digit
    @constraint(model, d in MOI.AllDifferent(8))
    # SEND and MORE start with S and M, MONEY with M, so neither is zero
    @constraint(model, s >= 1)
    @constraint(model, m >= 1)
    # SEND + MORE = MONEY, each word read as a number
    @constraint(model, 1000 * s + 100 * e + 10 * n + dd + 1000 * m + 100 * o + 10 * r + e ==
                       10000 * m + 1000 * o + 100 * n + 10 * e + y)
    return model, Dict("s" => s, "e" => e, "n" => n, "d" => dd, "m" => m, "o" => o, "r" => r, "y" => y)
end
