# Football squad: buy players for as close to GBP 30 million as possible without
# going over, taking the required number from each position and at least eleven
# players in all. The answer is the total price in GBP thousands.
using JuMP

function build(instance)
    # The players on offer are fixed by the problem: prices in GBP thousands.
    budget = 30000
    goalkeepers = [730, 1280, 3880]                                          # exactly 1
    defenders = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]              # 2 or more
    midfielders = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]  # 3 or more
    strikers = [4460, 6470, 7780, 8390, 9500]                                # 2 or more
    model = Model()
    g = @variable(model, [1:length(goalkeepers)], Bin)
    d = @variable(model, [1:length(defenders)], Bin)
    m = @variable(model, [1:length(midfielders)], Bin)
    s = @variable(model, [1:length(strikers)], Bin)
    @constraint(model, sum(g) == 1)
    @constraint(model, sum(d) >= 2)
    @constraint(model, sum(m) >= 3)
    @constraint(model, sum(s) >= 2)
    @constraint(model, sum(g) + sum(d) + sum(m) + sum(s) >= 11)
    @variable(model, 0 <= z <= budget, Int)
    @constraint(model, z == goalkeepers' * g + defenders' * d + midfielders' * m + strikers' * s)
    @objective(model, Max, z)
    return model, Dict("z" => z)
end
