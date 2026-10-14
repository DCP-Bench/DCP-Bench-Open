# Frog circle: cards 1..n are arranged in a circle. A frog starts on the card at
# position 0 (which holds card 1) and, from a card k, jumps k places clockwise, forever.
# Find an arrangement in which the frog lands on every card.
using JuMP

function build(instance)
    n = instance["n"]   # number of cards

    model = Model()

    # on[p, v] = 1 when position p (numbered 1..n here, position 0 of the circle is 1)
    # holds card v. The cards are a permutation of 1..n and card 1 is at the start.
    @variable(model, on[1:n, 1:n], Bin)
    @constraint(model, [p = 1:n], sum(on[p, v] for v in 1:n) == 1)
    @constraint(model, [v = 1:n], sum(on[p, v] for p in 1:n) == 1)
    @constraint(model, on[1, 1] == 1)

    # The frog must land on n different positions, starting at position 0, so after n - 1
    # jumps it has visited every position. The card n makes the frog jump all the way round
    # to where it is, so it can only sit on the last position visited. To state "the walk from
    # position 0 visits every position" as one cycle, the jump from the card n is read as a
    # jump back to position 0 (the last position leads back to the start); the n jumps then
    # have to form a single cycle through all positions.
    # arc[p, q] = 1 when the frog jumps from position p to position q (q = 1 is position 0
    # of the circle). A position p (0-based p - 1) holding card v jumps to (p - 1 + v) mod n.
    arc = Matrix{AffExpr}(undef, n, n)
    for p in 1:n, q in 1:n
        arc[p, q] = AffExpr(0.0)
    end
    for p in 1:n, v in 1:n
        q = v == n ? 1 : mod(p - 1 + v, n) + 1
        add_to_expression!(arc[p, q], on[p, v])
    end

    # every position is jumped to exactly once (each position already has one jump, from
    # the card it holds)
    @constraint(model, [q = 1:n], sum(arc[p, q] for p in 1:n) == 1)

    # The jumps form one cycle and not several (Miller-Tucker-Zemlin): visit[p] = the step at
    # which the frog is on position p; each jump, other than the closing one back to
    # position 0, goes to a later step. The big-M is n, the largest step difference plus one.
    @variable(model, 0 <= visit[1:n] <= n - 1, Int)
    @constraint(model, visit[1] == 0)
    for p in 1:n, q in 2:n
        @constraint(model, visit[q] >= visit[p] + 1 - n * (1 - arc[p, q]))
    end

    # x[p] = the card at position p (declared output)
    x = [sum(v * on[p, v] for v in 1:n) for p in 1:n]
    return model, Dict("x" => x)
end
