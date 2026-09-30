# Fancy dress: Mr Greenguest owns a green shirt and can buy a green tie ($10), a
# green hat ($2) and green socks ($12). A guest who breaks a dress rule pays an
# $11 entrance fee. Find the cheapest way in.
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    # t tie, h hat, r shirt, s socks, n entrance fee; 1 when chosen
    @variable(model, t, Bin); @variable(model, h, Bin); @variable(model, r, Bin)
    @variable(model, s, Bin); @variable(model, n, Bin)
    # 1. a green tie needs a green shirt (or the fee): not t, or r, or n
    @constraint(model, (1 - t) + r + n >= 1)
    # 2. green socks or a green shirt need a green tie or a green hat (or the fee):
    #    for each of s and r, not it, or t, or h, or n
    @constraint(model, (1 - s) + t + h + n >= 1)
    @constraint(model, (1 - r) + t + h + n >= 1)
    # 3. a green shirt, a green hat or no green socks need a green tie or the fee
    @constraint(model, (1 - r) + t + n >= 1)
    @constraint(model, (1 - h) + t + n >= 1)
    @constraint(model, s + t + n >= 1)
    @objective(model, Min, 10 * t + 2 * h + 12 * s + 11 * n)
    return model, Dict("t" => t, "h" => h, "r" => r, "s" => s, "n" => n)
end
