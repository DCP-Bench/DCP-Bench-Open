# Solitaire battleships: fill a grid with water, submarines and the parts of longer
# ships (left, right, top, bottom, middle) so that the fleet is complete, no two ships
# touch (not even diagonally), and the row and column counts of ship squares hold.
using JuMP

function build(instance)
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]              # ship squares wanted in each row
    colsum = instance["colsum"]              # ship squares wanted in each column
    fleet = Dict(f[1] => f[2] for f in instance["fleet_counts"])   # ship size => number of ships
    hints = instance["hints"]                # [row, col, cell value], 0-based positions
    # the codes of the cell values, as the instance defines them
    WATER, SHIP, CIRCLE = instance["WATER"], instance["_SHIP"], instance["CIRCLE"]
    LEFT, RIGHT, TOP = instance["LEFT"], instance["RIGHT"], instance["TOP"]
    BOTTOM, MIDDLE = instance["BOTTOM"], instance["MIDDLE"]
    # The cell values a square can take. The generic code `_SHIP` is not used: every ship
    # square is a submarine or one of the five typed parts of a longer ship.
    values = [WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]

    model = Model()

    # g[r, c, v] = 1 when square (r, c) holds value v; exactly one value per square.
    @variable(model, g[r = 1:rows, c = 1:cols, v = values], Bin)
    @constraint(model, [r = 1:rows, c = 1:cols], sum(g[r, c, v] for v in values) == 1)
    inside(r, c) = 1 <= r <= rows && 1 <= c <= cols
    # ship(r, c) is 1 when the square is part of a ship, i.e. is not water
    ship(r, c) = 1 - g[r, c, WATER]

    # Hints: squares whose content is given (0-based position in the instance)
    for (r, c, v) in hints
        if v == SHIP
            @constraint(model, ship(r + 1, c + 1) == 1)
        else
            @constraint(model, g[r+1, c+1, v] == 1)
        end
    end

    # The digits beside the grid: number of ship squares in each row and each column
    @constraint(model, [r = 1:rows], sum(ship(r, c) for c in 1:cols) == rowsum[r])
    @constraint(model, [c = 1:cols], sum(ship(r, c) for r in 1:rows) == colsum[c])

    # No two ships touch diagonally: two diagonal neighbours are not both ship squares
    for r in 1:rows, c in 1:cols, d in ((1, 1), (1, -1))
        if inside(r + d[1], c + d[2])
            @constraint(model, ship(r, c) + ship(r + d[1], c + d[2]) <= 1)
        end
    end

    dirs = ((0, 1), (0, -1), (1, 0), (-1, 0))   # right, left, down, up

    # A submarine (circle) is surrounded by water on all four sides
    for r in 1:rows, c in 1:cols, d in dirs
        if inside(r + d[1], c + d[2])
            @constraint(model, g[r, c, CIRCLE] <= g[r+d[1], c+d[2], WATER])
        end
    end

    # The end pieces of a longer ship. Each continues in its body direction with a middle
    # part or the opposite end, and has water on its other three sides. A piece at the
    # edge of the grid cannot continue in a direction that leaves the grid.
    #               piece   body direction  what must follow
    ends = ((LEFT,   (0, 1),  (MIDDLE, RIGHT)),
            (RIGHT,  (0, -1), (MIDDLE, LEFT)),
            (TOP,    (1, 0),  (MIDDLE, BOTTOM)),
            (BOTTOM, (-1, 0), (MIDDLE, TOP)))
    for r in 1:rows, c in 1:cols, (piece, body, follow) in ends
        if !inside(r + body[1], c + body[2])
            @constraint(model, g[r, c, piece] == 0)
        end
        for d in dirs
            rr, cc = r + d[1], c + d[2]
            if !inside(rr, cc)
                continue
            elseif d == body
                @constraint(model, g[r, c, piece] <= sum(g[rr, cc, k] for k in follow))
            else
                @constraint(model, g[r, c, piece] <= g[rr, cc, WATER])
            end
        end
    end

    # A middle part lies inside a horizontal or a vertical ship. horizontal[r, c] = 1 when
    # it has a left part or middle on its left, a right part or middle on its right, and
    # water above and below; vertical[r, c] likewise with the roles of the axes swapped.
    horizontal = @variable(model, [1:rows, 1:cols], Bin)
    vertical = @variable(model, [1:rows, 1:cols], Bin)
    for r in 1:rows, c in 1:cols
        @constraint(model, g[r, c, MIDDLE] == horizontal[r, c] + vertical[r, c])
        if inside(r, c - 1) && inside(r, c + 1)
            @constraint(model, horizontal[r, c] <= g[r, c-1, LEFT] + g[r, c-1, MIDDLE])
            @constraint(model, horizontal[r, c] <= g[r, c+1, RIGHT] + g[r, c+1, MIDDLE])
            for d in ((1, 0), (-1, 0))
                inside(r + d[1], c) && @constraint(model, horizontal[r, c] <= g[r+d[1], c, WATER])
            end
        else
            @constraint(model, horizontal[r, c] == 0)
        end
        if inside(r - 1, c) && inside(r + 1, c)
            @constraint(model, vertical[r, c] <= g[r-1, c, TOP] + g[r-1, c, MIDDLE])
            @constraint(model, vertical[r, c] <= g[r+1, c, BOTTOM] + g[r+1, c, MIDDLE])
            for d in ((0, 1), (0, -1))
                inside(r, c + d[2]) && @constraint(model, vertical[r, c] <= g[r, c+d[2], WATER])
            end
        else
            @constraint(model, vertical[r, c] == 0)
        end
    end

    # Fleet: the number of submarines (ships of size 1)
    @constraint(model, sum(g[r, c, CIRCLE] for r in 1:rows, c in 1:cols) == fleet[1])

    # Fleet: the number of ships of each longer size. A ship of size s is a left part and a
    # right part s-1 squares apart in a row with middles between (or top, bottom and middles
    # in a column). placed = 1 exactly when all these squares have the required parts
    # (and-linearisation: at most each part, and at least their sum minus (s - 1)).
    for (size, count) in fleet
        size >= 2 || continue
        placed = AffExpr[]
        for r in 1:rows, c in 1:cols
            for (head, tail, along) in ((LEFT, RIGHT, (0, 1)), (TOP, BOTTOM, (1, 0)))
                inside(r + (size - 1) * along[1], c + (size - 1) * along[2]) || continue
                parts = [g[r, c, head], g[r+(size-1)*along[1], c+(size-1)*along[2], tail]]
                for k in 1:size-2
                    push!(parts, g[r+k*along[1], c+k*along[2], MIDDLE])
                end
                p = @variable(model, binary = true)
                @constraint(model, [q in parts], p <= q)
                @constraint(model, p >= sum(parts) - (size - 1))
                push!(placed, 1 * p)
            end
        end
        @constraint(model, sum(placed) == count)
    end

    # Fleet: no ship of a size the fleet does not list. Every left or top end starts one of
    # the ships counted above, so their number equals the number of longer ships.
    @constraint(model, sum(g[r, c, LEFT] + g[r, c, TOP] for r in 1:rows, c in 1:cols) ==
                       sum(count for (size, count) in fleet if size > 1))

    # the grid of cell values (declared output), read off the one-hot variables
    grid = [sum(v * g[r, c, v] for v in values) for r in 1:rows, c in 1:cols]
    return model, Dict("grid" => grid)
end
