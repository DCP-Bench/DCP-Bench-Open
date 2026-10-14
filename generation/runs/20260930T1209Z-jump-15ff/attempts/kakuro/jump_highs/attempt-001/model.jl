# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue with no digit repeated in it.
# Blank cells hold 0.
using JuMP

function build(instance)
    n = instance["n"]
    entries = instance["problem"]   # [clue, [row, col], [row, col], ...], 1-based
    blanks = instance["blanks"]     # [row, col] of the blank cells
    model = Model()
    @variable(model, 0 <= x[1:n, 1:n] <= 9, Int)
    # has[i, j, d] = 1 when cell (i, j) holds the digit d (none for a 0)
    @variable(model, has[1:n, 1:n, 1:9], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(has[i, j, :]) <= 1)
    @constraint(model, [i = 1:n, j = 1:n], x[i, j] == sum(d * has[i, j, d] for d in 1:9))
    for cell in blanks
        fix(x[cell[1], cell[2]], 0; force = true)
    end
    for entry in entries
        clue, cells = entry[1], entry[2:end]
        # the cells of an entry hold digits 1..9 that add up to the clue ...
        for cell in cells
            @constraint(model, sum(has[cell[1], cell[2], :]) == 1)
        end
        @constraint(model, sum(x[cell[1], cell[2]] for cell in cells) == clue)
        # ... and are all different
        @constraint(model, [d = 1:9], sum(has[cell[1], cell[2], d] for cell in cells) <= 1)
    end
    return model, Dict("x" => x)
end
