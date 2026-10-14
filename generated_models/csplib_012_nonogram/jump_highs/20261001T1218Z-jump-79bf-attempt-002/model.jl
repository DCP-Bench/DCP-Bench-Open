# Nonogram: shade cells of a grid so that the shaded runs in every row and column
# are exactly the block lengths given for that line, in order, with at least one
# unshaded cell between consecutive blocks. A rule entry of 0 is padding.
using JuMP

# The cells of one line of length len as linear expressions in fresh start
# variables: start[j][p] = 1 when block j begins at cell p. Block j can begin
# no earlier than the blocks before it (plus one gap each) allow, and no later
# than the blocks after it (plus one gap each) allow; those two limits are the
# bounds of p. This is a MIP stand-in for a regular (automaton) constraint.
function line_cells(model, len, rule)
    blocks = [b for b in rule if b > 0]      # padding zeros dropped
    k = length(blocks)
    # earliest and latest start of each block
    lo = [1 + sum(blocks[i] + 1 for i in 1:j-1; init = 0) for j in 1:k]
    hi = [len - blocks[j] + 1 - sum(blocks[i] + 1 for i in j+1:k; init = 0) for j in 1:k]
    start = [@variable(model, [lo[j]:hi[j]], Bin) for j in 1:k]
    # each block starts exactly once
    for j in 1:k
        @constraint(model, sum(start[j]) == 1)
    end
    # block j+1 starts after block j has ended and left a gap:
    # for every q, if block j+1 starts at or before q then block j started at or before q - b_j - 1
    for j in 1:k-1, q in lo[j+1]:hi[j+1]
        early = [p for p in lo[j]:hi[j] if p <= q - blocks[j] - 1]
        @constraint(model, sum(start[j+1][p] for p in lo[j+1]:q) <=
                           sum(start[j][p] for p in early; init = 0))
    end
    # cell c is shaded exactly when some block covers it
    return [sum(start[j][p] for j in 1:k for p in max(lo[j], c - blocks[j] + 1):min(hi[j], c); init = 0)
            for c in 1:len]
end

function build(instance)
    rows, cols = instance["rows"], instance["cols"]
    row_rules = instance["row_rules"]   # row_rules[r] = block lengths of row r (0 = padding)
    col_rules = instance["col_rules"]   # col_rules[c] = block lengths of column c

    model = Model()
    # board[r, c] = 1 for a shaded cell
    @variable(model, board[1:rows, 1:cols], Bin)

    # the shaded runs of each row are its blocks
    for r in 1:rows
        cells = line_cells(model, cols, row_rules[r])
        @constraint(model, [c = 1:cols], board[r, c] == cells[c])
    end
    # the shaded runs of each column are its blocks
    for c in 1:cols
        cells = line_cells(model, rows, col_rules[c])
        @constraint(model, [r = 1:rows], board[r, c] == cells[r])
    end

    return model, Dict("board" => board)
end
