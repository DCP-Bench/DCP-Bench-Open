# Handshaking: Hilary and Jocelyn host some couples. Nobody shakes hands with
# themselves or their spouse, and everybody except Hilary shook a different
# number of hands. How many hands did Hilary shake?
using JuMP

function build(instance)
    couples = instance["num_couples"]
    n = 2 + 2 * couples      # Hilary is person 1, Jocelyn 2; spouses are 2k - 1 and 2k
    model = Model()
    # shook[i, j] for i < j: 1 when i and j shook hands; spouses never do
    @variable(model, shook[i = 1:n, j = i+1:n], Bin)
    for k in 1:div(n, 2)
        fix(shook[2k - 1, 2k], 0; force = true)
    end
    handshake(i, j) = i < j ? shook[i, j] : shook[j, i]
    @variable(model, 0 <= x[1:n] <= n - 2, Int)
    @constraint(model, [i = 1:n], x[i] == sum(handshake(i, j) for j in 1:n if j != i))
    # all answers except Hilary's differ
    @constraint(model, x[2:n] in MOI.AllDifferent(n - 1))
    return model, Dict("hil" => x[1])
end
