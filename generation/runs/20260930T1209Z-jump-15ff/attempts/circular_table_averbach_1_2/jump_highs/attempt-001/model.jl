# Averbach's card-passing riddle: X, Y and Z, of three nationalities (American,
# English, French), sit round a table, each passing cards to the person on their
# right. Y passed to the American, and X passed to the person who passed to the
# Frenchwoman. Seats are 0, 1, 2; seat s + 1 (mod 3) is to the right of s.
using JuMP

function build(instance)
    # The riddle fixes everything; the instance carries no data.
    model = Model()
    @variable(model, 0 <= players[1:3] <= 2, Int)
    @variable(model, 0 <= nations[1:3] <= 2, Int)
    x, y, z = players
    american, english, french = nations
    @constraint(model, players in MOI.AllDifferent(3))
    @constraint(model, nations in MOI.AllDifferent(3))
    # "a is to the right of b": a = b + 1 - 3 * wrap, wrap = 1 when b is the last seat
    @variable(model, wrap[1:2], Bin)
    # Y passed to the American: the American sits to the right of Y
    @constraint(model, american == y + 1 - 3 * wrap[1])
    # X passed to the person who passed to the Frenchwoman: X sits to her right
    @constraint(model, x == french + 1 - 3 * wrap[2])
    return model, Dict("x" => x, "y" => y, "z" => z,
                       "american" => american, "english" => english, "french" => french)
end
