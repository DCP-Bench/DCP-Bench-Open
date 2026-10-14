# Crypta: a cryptarithmetic addition of two 20-digit numbers. Each letter is a
# different digit from 0 to 9, and no number starts with a zero.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    first_word = "BAIJJAJIIAHFCFEBBJEA"
    second_word = "DHFGABCDIDBIFFAGFEJE"
    total = "GJEGACDDHFAFJBFIHEEF"
    letters = collect("ABCDEFGHIJ")
    index = Dict(letter => i for (i, letter) in enumerate(letters))
    width = length(total)
    model = Model()
    @variable(model, 0 <= d[1:10] <= 9, Int)
    @constraint(model, d in MOI.AllDifferent(10))
    # no number starts with a zero
    for word in (first_word, second_word, total)
        @constraint(model, d[index[word[1]]] >= 1)
    end
    # the addition column by column, units first; carry[k] comes into column k
    @variable(model, 0 <= carry[1:width+1] <= 1, Int)
    fix(carry[1], 0; force = true)
    fix(carry[width + 1], 0; force = true)
    for k in 1:width
        p = width - k + 1
        @constraint(model, d[index[first_word[p]]] + d[index[second_word[p]]] + carry[k] ==
                           d[index[total[p]]] + 10 * carry[k + 1])
    end
    return model, Dict(string(letter) => d[index[letter]] for letter in letters)
end
