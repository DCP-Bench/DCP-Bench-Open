# Crossword: choose different words from a list of 15 for the 8 numbered slots
# of a small grid so that every crossing shows the same letter in both words.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    words = ["HOSES", "LASER", "SAILS", "SHEET", "STEER", "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
             "AFT", "ALE", "EEL", "LEE", "TIE"]
    nw = length(words)
    # letters as numbers A = 1 .. Z = 26, padded with 0 up to five letters
    letter(w, p) = p <= length(words[w]) ? Int(words[w][p]) - Int('A') + 1 : 0
    # each crossing: slot a, letter position in a, slot b, letter position in b (0-based)
    crossings = [(0, 2, 1, 0), (0, 4, 2, 0), (3, 1, 1, 2), (3, 2, 4, 0), (3, 3, 2, 2), (6, 0, 1, 3),
                 (6, 1, 4, 1), (6, 2, 2, 3), (7, 0, 5, 1), (7, 2, 1, 4), (7, 3, 4, 2), (7, 4, 2, 4)]
    model = Model()
    # E[s] = the 0-based index of the word in slot s; all slots get different words
    @variable(model, 0 <= E[1:8] <= nw - 1, Int)
    @constraint(model, E in MOI.AllDifferent(8))
    for (a, pa, b, pb) in crossings
        pairs = [(wa - 1, wb - 1) for wa in 1:nw for wb in 1:nw if letter(wa, pa + 1) == letter(wb, pb + 1)]
        table = Float64[p[k] for p in pairs, k in 1:2]
        @constraint(model, [E[a + 1], E[b + 1]] in MOI.Table(table))
    end
    return model, Dict("E" => E)
end
