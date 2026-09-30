# The abbot's puzzle: 100 bushels among 100 people, three bushels to a man, two
# to a woman and half a bushel to a child, with five times as many women as men.
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    @variable(model, 0 <= men <= 100, Int)
    @variable(model, 0 <= women <= 100, Int)
    @variable(model, 0 <= children <= 100, Int)
    @constraint(model, men + women + children == 100)
    @constraint(model, 6 * men + 4 * women + children == 200)   # in half bushels
    @constraint(model, 5 * men == women)
    return model, Dict("men" => men, "women" => women, "children" => children)
end
