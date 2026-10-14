# Building blocks: put each letter of the alphabet on one side of one of
# num_blocks alphabet blocks, with num_sides letters on every block, so that each
# word of the list can be spelled by taking its letters from different blocks.
using JuMP

function build(instance)
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]       # letters on each block
    alphabet = instance["alphabet"]         # the letters to place, in order
    words_str = instance["words_str"]       # the words that must be spelled
    num_letters = length(alphabet)

    # position of each letter in the alphabet (1-based here)
    letter_index = Dict(c => i for (i, c) in enumerate(alphabet))
    words = [[letter_index[c] for c in w] for w in words_str]

    model = Model()

    # on_block[l, b] = 1 when letter l is on block b
    @variable(model, on_block[1:num_letters, 1:num_blocks], Bin)
    # each letter is on exactly one block
    @constraint(model, [l = 1:num_letters], sum(on_block[l, :]) == 1)

    # dice[l] = the (0-based) block of letter l, a declared output
    @variable(model, 0 <= dice[1:num_letters] <= num_blocks - 1, Int)
    @constraint(model, [l = 1:num_letters],
                dice[l] == sum((b - 1) * on_block[l, b] for b in 1:num_blocks))

    # the letters of a word must be on different blocks: no block carries two of them
    # (counted per letter occurrence, so a repeated letter in a word cannot be spelled)
    for word in words, b in 1:num_blocks
        @constraint(model, sum(on_block[l, b] for l in word) <= 1)
    end

    # each block has exactly num_sides letters
    @constraint(model, [b = 1:num_blocks], sum(on_block[:, b]) == num_sides)

    return model, Dict("dice" => dice)
end
