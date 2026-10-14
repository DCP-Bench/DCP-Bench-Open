# Crossfigures: a numerical crossword. Fill a 9 by 9 grid with digits so that every across and
# every down word, read as a number, satisfies its clue (for example "27 across times two",
# "five dozen", "a square number", "a prime number"). Black squares hold 0 in the printout.
using JuMP

function build(instance)
    # The puzzle (grid, words and clues) is fixed by the problem; the instance carries no data.
    n = 9

    # The grid, as the problem draws it: '#' is a black square, '.' a square that takes a digit.
    layout = ["....#....",
              "..#...#..",
              ".#..#..#.",
              "....#....",
              "#.#####.#",
              "....#....",
              ".#..#..#.",
              "..#...#..",
              "....#...."]

    # Words as number => (length, row, column of the first digit), numbered as in the problem.
    across_words = Dict(1 => (4, 1, 1), 4 => (4, 1, 6), 7 => (2, 2, 1), 8 => (3, 2, 4),
                        9 => (2, 2, 8), 10 => (2, 3, 3), 11 => (2, 3, 6), 13 => (4, 4, 1),
                        15 => (4, 4, 6), 17 => (4, 6, 1), 20 => (4, 6, 6), 23 => (2, 7, 3),
                        24 => (2, 7, 6), 25 => (2, 8, 1), 27 => (3, 8, 4), 28 => (2, 8, 8),
                        29 => (4, 9, 1), 30 => (4, 9, 6))
    down_words = Dict(1 => (4, 1, 1), 2 => (2, 1, 2), 3 => (4, 1, 4), 4 => (4, 1, 6),
                      5 => (2, 1, 8), 6 => (4, 1, 9), 10 => (2, 3, 3), 12 => (2, 3, 7),
                      14 => (3, 4, 2), 16 => (3, 4, 8), 17 => (4, 6, 1), 18 => (2, 6, 3),
                      19 => (4, 6, 4), 20 => (4, 6, 6), 21 => (2, 6, 7), 22 => (4, 6, 9),
                      26 => (2, 8, 2), 28 => (2, 8, 8))

    model = Model()

    # M[i, j] = the digit in square (i, j); black squares are 0
    @variable(model, 0 <= M[1:n, 1:n] <= 9, Int)
    for i in 1:n, j in 1:n
        if layout[i][j] == '#'
            @constraint(model, M[i, j] == 0)
        end
    end

    # Each word is the number its digits spell: A[k] for "k across", D[k] for "k down".
    A = Dict(k => sum(10^(len - 1 - t) * M[r, c+t] for t in 0:len-1)
             for (k, (len, r, c)) in across_words)
    D = Dict(k => sum(10^(len - 1 - t) * M[r+t, c] for t in 0:len-1)
             for (k, (len, r, c)) in down_words)

    # member_of(x, candidates): x takes one of the listed values. One binary per candidate, one
    # of them is on, and x is the sum of candidate * binary. Returns the binaries.
    function member_of(x, candidates)
        pick = @variable(model, [1:length(candidates)], Bin)
        @constraint(model, sum(pick) == 1)
        @constraint(model, x == sum(c * pick[k] for (k, c) in enumerate(candidates)))
        return pick
    end

    # times_member(pick, candidates, y, U) = (the chosen candidate) * y for a quantity
    # 0 <= y <= U: the sum over candidates c of c * (pick[k] * y), each binary-times-bounded
    # product linearised with a helper z (z = y when the candidate is picked, else 0).
    function times_member(pick, candidates, y, U)
        z = @variable(model, [1:length(candidates)], lower_bound = 0, upper_bound = U)
        for k in eachindex(candidates)
            @constraint(model, z[k] <= U * pick[k])
            @constraint(model, z[k] <= y)
            @constraint(model, z[k] >= y - U * (1 - pick[k]))
        end
        return sum(c * z[k] for (k, c) in enumerate(candidates))
    end

    # A word of `len` digits is at most 10^len - 1; squares and primes are listed up to that.
    limit(len) = 10^len - 1
    squares(len) = [i^2 for i in 1:isqrt(limit(len))]
    primes(len) = [p for p in 2:limit(len) if all(p % d != 0 for d in 2:isqrt(p))]

    # Across clues
    # 1: 27 across times two
    @constraint(model, A[1] == 2 * A[27])
    # 4: 4 down plus seventy-one
    @constraint(model, A[4] == D[4] + 71)
    # 7: 18 down plus four
    @constraint(model, A[7] == D[18] + 4)
    # 8: 6 down divided by sixteen
    @constraint(model, 16 * A[8] == D[6])
    # 9: 2 down minus eighteen
    @constraint(model, A[9] == D[2] - 18)
    # 10: a dozen in six gross
    @constraint(model, 12 * A[10] == 6 * 144)
    # 11: 5 down minus seventy
    @constraint(model, A[11] == D[5] - 70)
    # 15: 6 down minus 350
    @constraint(model, A[15] == D[6] - 350)
    # 20: a square number
    member_of(A[20], squares(4))
    # 23: a prime number
    primes_23 = primes(2)
    prime_23 = member_of(A[23], primes_23)
    # 24: a square number
    member_of(A[24], squares(2))
    # 25: 20 across divided by seventeen
    @constraint(model, 17 * A[25] == A[20])
    # 27: 6 down divided by four
    @constraint(model, 4 * A[27] == D[6])
    # 28: four dozen
    @constraint(model, A[28] == 4 * 12)
    # 29: seven gross
    @constraint(model, A[29] == 7 * 144)
    # 30: 22 down plus 450
    @constraint(model, A[30] == D[22] + 450)

    # The clues that multiply two unknown numbers. Both involve the prime 23 across, so it is
    # multiplied through its candidate binaries.
    # 13: 26 down times 23 across, where 26 down is five times 24 across (below)
    @constraint(model, A[13] == times_member(prime_23, primes_23, D[26], 99))
    # 17: 25 across times 23 across
    @constraint(model, A[17] == times_member(prime_23, primes_23, A[25], 99))
    # 6 down: 28 across times 23 across, with 28 across fixed to four dozen
    @constraint(model, D[6] == (4 * 12) * A[23])

    # Down clues
    # 1: 1 across plus twenty-seven
    @constraint(model, D[1] == A[1] + 27)
    # 2: five dozen
    @constraint(model, D[2] == 5 * 12)
    # 3: 30 across plus 888
    @constraint(model, D[3] == A[30] + 888)
    # 4: two times 17 across
    @constraint(model, D[4] == 2 * A[17])
    # 5: 29 across divided by twelve
    @constraint(model, 12 * D[5] == A[29])
    # 10: 10 across plus four
    @constraint(model, D[10] == A[10] + 4)
    # 12: three times 24 across
    @constraint(model, D[12] == 3 * A[24])
    # 14: 13 across divided by sixteen
    @constraint(model, 16 * D[14] == A[13])
    # 16: 28 down times fifteen
    @constraint(model, D[16] == 15 * D[28])
    # 17: 13 across minus 399
    @constraint(model, D[17] == A[13] - 399)
    # 18: 29 across divided by eighteen
    @constraint(model, 18 * D[18] == A[29])
    # 19: 22 down minus ninety-four
    @constraint(model, D[19] == D[22] - 94)
    # 20: 20 across minus nine
    @constraint(model, D[20] == A[20] - 9)
    # 21: 25 across minus fifty-two
    @constraint(model, D[21] == A[25] - 52)
    # 22: 20 down times six
    @constraint(model, D[22] == 6 * D[20])
    # 26: five times 24 across
    @constraint(model, D[26] == 5 * A[24])
    # 28: 21 down plus twenty-seven
    @constraint(model, D[28] == D[21] + 27)

    return model, Dict("M" => M)
end
