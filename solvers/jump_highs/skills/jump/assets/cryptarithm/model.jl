# Cryptarithm SEND + MORE = MONEY: each letter is a distinct digit, leading letters are not 0.
using JuMP, HiGHS

addends = ["SEND", "MORE"]
total = "MONEY"

letters = sort(unique(collect(join(addends) * total)))
idx = Dict(ch => i for (i, ch) in enumerate(letters))

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, 0 <= d[1:length(letters)] <= 9, Int)     # d[idx[ch]] = digit of letter ch
@constraint(model, d in MOI.AllDifferent(length(letters)))  # distinct letters, distinct digits

for w in vcat(addends, [total])
    @constraint(model, d[idx[w[1]]] >= 1)                  # no number starts with 0
end

# A word's value is its digits weighted by powers of ten: E N D -> 100 E + 10 N + D.
word_value(w) = sum(10^(length(w) - k) * d[idx[w[k]]] for k in 1:length(w))
@constraint(model, sum(word_value(w) for w in addends) == word_value(total))

optimize!(model)
println("Status: ", termination_status(model))
if has_values(model)
    digit = Dict(ch => round(Int, value(d[idx[ch]])) for ch in letters)
    println(join(["$ch=$(digit[ch])" for ch in letters], " "))
    println("Check: ", sum(sum(10^(length(w) - k) * digit[w[k]] for k in 1:length(w)) for w in addends) ==
                       sum(10^(length(total) - k) * digit[total[k]] for k in 1:length(total)))
end
