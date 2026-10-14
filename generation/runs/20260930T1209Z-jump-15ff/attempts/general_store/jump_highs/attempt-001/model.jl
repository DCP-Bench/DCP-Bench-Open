# General store: each letter of the sign stands for a different digit, and the
# sixteen words above the line add up to ALL WOOL.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"
    letters = sort(unique(join(words) * total))
    index = Dict(letter => i for (i, letter) in enumerate(letters))
    width = length(total)
    model = Model()
    @variable(model, 0 <= d[1:length(letters)] <= 9, Int)
    # every letter stands for a different digit
    @constraint(model, d in MOI.AllDifferent(length(letters)))
    # the addition column by column, units first; carry[k] comes into column k,
    # at most 15 since a column adds sixteen digits
    @variable(model, 0 <= carry[1:width+1] <= 15, Int)
    fix(carry[1], 0; force = true)
    fix(carry[width + 1], 0; force = true)
    for k in 1:width
        column = [d[index[w[end - k + 1]]] for w in words if length(w) >= k]
        @constraint(model, sum(column) + carry[k] == d[index[total[end - k + 1]]] + 10 * carry[k + 1])
    end
    return model, Dict(string(letter) => d[index[letter]] for letter in letters)
end
