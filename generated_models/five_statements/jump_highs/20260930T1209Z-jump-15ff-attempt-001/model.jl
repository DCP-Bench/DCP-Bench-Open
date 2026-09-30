# Five statements: statement i says "exactly i of these statements are false".
# Which are true?
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    @variable(model, statements[1:5], Bin)
    # is_false[k + 1] = 1 when exactly k statements are false
    @variable(model, is_false[1:6], Bin)
    @constraint(model, sum(is_false) == 1)
    @constraint(model, 5 - sum(statements) == sum((k - 1) * is_false[k] for k in 1:6))
    # statement i is true exactly when i statements are false
    @constraint(model, [i = 1:5], statements[i] == is_false[i + 1])
    return model, Dict("statements" => statements)
end
