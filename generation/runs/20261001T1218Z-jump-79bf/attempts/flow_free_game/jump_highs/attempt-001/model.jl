# Flow Free: connect matching colours with pipes and cover the entire board. Cells given a
# colour are the pipe ends; a pipe end touches exactly one cell of its colour and every
# other cell touches exactly two cells of its own colour (the pipe passes through it).
using JuMP

function build(instance)
    board = instance["board"]   # board[i][j] = colour of an end at row i, column j, or 0
    M = length(board)
    N = length(board[1])
    colors = 10   # colours are the integers 1..10 (the problem's domain for a cell)

    model = Model()

    # at[i, j, k] = 1 when cell (i, j) has colour k; B[i, j] is that colour, the declared output
    @variable(model, at[1:M, 1:N, 1:colors], Bin)
    @constraint(model, [i = 1:M, j = 1:N], sum(at[i, j, :]) == 1)
    @variable(model, 1 <= B[1:M, 1:N] <= colors, Int)
    @constraint(model, [i = 1:M, j = 1:N], B[i, j] == sum(k * at[i, j, k] for k in 1:colors))

    # same = 1 exactly when two neighbouring cells (sharing a side) have the same colour: if both
    # have colour k then same is 1, and if same is 1 then every colour k is held by both cells
    # or by neither. Each cell collects the binaries of its sides in sides[i, j].
    sides = [VariableRef[] for i in 1:M, j in 1:N]
    for i in 1:M, j in 1:N, (di, dj) in ((0, 1), (1, 0))
        p, q = i + di, j + dj
        if p <= M && q <= N
            same = @variable(model, binary = true)
            for k in 1:colors
                @constraint(model, same >= at[i, j, k] + at[p, q, k] - 1)
                @constraint(model, same <= 1 - at[i, j, k] + at[p, q, k])
                @constraint(model, same <= 1 - at[p, q, k] + at[i, j, k])
            end
            push!(sides[i, j], same)
            push!(sides[p, q], same)
        end
    end

    for i in 1:M, j in 1:N
        if board[i][j] != 0
            # a pipe end has its given colour and exactly one neighbour of the same colour
            @constraint(model, B[i, j] == board[i][j])
            @constraint(model, sum(sides[i, j]) == 1)
        else
            # an empty cell is filled with a colour shared by exactly two of its neighbours.
            # (The problem also allows "colour 0 means empty", but a cell's colour is 1..10,
            # so that branch can never hold.)
            @constraint(model, sum(sides[i, j]) == 2)
        end
    end

    return model, Dict("B" => B)
end
