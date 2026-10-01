# Word design for DNA computing: find num_words words of length n over the
# alphabet {A, C, G, T} (coded 1, 2, 3, 4) such that every word has exactly 4
# letters from {C, G}, any two distinct words differ in at least 4 positions, and
# for any two words x and y (possibly the same word) the reverse of x and the
# Watson-Crick complement of y (A<->T, C<->G, i.e. letter l becomes 5 - l)
# differ in at least 4 positions.
using JuMP

function build(instance)
    n = instance["n"]                  # length of each word
    num_words = instance["num_words"]  # number of words to find
    # Constants of the problem statement, not of the instance (mirrored from the reference)
    gc_count = 4                       # letters from {C, G} in each word
    min_distance = 4                   # required number of differing positions
    A, C, G, T = 1, 2, 3, 4

    model = Model()

    # is_letter[w, j, l] = 1 when letter j of word w is l
    @variable(model, is_letter[1:num_words, 1:n, 1:T], Bin)
    @constraint(model, [w = 1:num_words, j = 1:n], sum(is_letter[w, j, :]) == 1)

    # words[w, j] = the letter at position j of word w, a declared output
    @variable(model, A <= words[1:num_words, 1:n] <= T, Int)
    @constraint(model, [w = 1:num_words, j = 1:n],
                words[w, j] == sum(l * is_letter[w, j, l] for l in A:T))

    # every word has exactly 4 symbols from {C, G}
    @constraint(model, [w = 1:num_words],
                sum(is_letter[w, j, C] + is_letter[w, j, G] for j in 1:n) == gc_count)

    # Distinct words differ in at least 4 positions: differ[x, y, j] may be 1 only
    # if the two words have different letters at j (when both hold letter l, it
    # is forced to 0), and at least 4 positions must have it at 1.
    for x in 1:num_words-1, y in x+1:num_words
        differ = @variable(model, [1:n], Bin)
        @constraint(model, [j = 1:n, l = A:T],
                    differ[j] + is_letter[x, j, l] + is_letter[y, j, l] <= 2)
        @constraint(model, sum(differ) >= min_distance)
    end

    # For every x and y (also x == y): the reverse of x, whose letter at position j
    # is x[n + 1 - j], and the complement of y, whose letter at j is 5 - y[j], differ in
    # at least 4 positions. They agree at j only when x[n + 1 - j] = l and y[j] = 5 - l.
    for x in 1:num_words, y in 1:num_words
        differ_rc = @variable(model, [1:n], Bin)
        @constraint(model, [j = 1:n, l = A:T],
                    differ_rc[j] + is_letter[x, n + 1 - j, l] + is_letter[y, j, A + T - l] <= 2)
        @constraint(model, sum(differ_rc) >= min_distance)
    end

    return model, Dict("words" => words)
end
