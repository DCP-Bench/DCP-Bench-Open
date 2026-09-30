# Set: choose three of the cards on the table (0-based indices) that form a set:
# for each of the four features (number, fill, colour, shape) the three cards
# show either the same value or three different values.
using JuMP

function build(instance)
    cards = instance["cards_data"]   # each card is [number, fill, colour, shape]
    nc = length(cards)
    model = Model()
    @variable(model, chosen[1:nc], Bin)
    @constraint(model, sum(chosen) == 3)
    # For each feature and value, the chosen cards showing that value number 0, 1
    # or 3, never 2: all the same, or all different.
    for f in 1:4, v in unique(card[f] for card in cards)
        count = sum(chosen[c] for c in 1:nc if cards[c][f] == v)
        three = @variable(model, binary = true)
        @constraint(model, count <= 1 + 2 * three)
        @constraint(model, count >= 3 * three)
    end
    # the chosen indices in increasing order: place[k, c] = 1 when card c is the k-th chosen
    @variable(model, place[1:3, 1:nc], Bin)
    @constraint(model, [k = 1:3], sum(place[k, :]) == 1)
    @constraint(model, [c = 1:nc], sum(place[:, c]) == chosen[c])
    @variable(model, 0 <= winning[1:3] <= nc - 1, Int)
    @constraint(model, [k = 1:3], winning[k] == sum((c - 1) * place[k, c] for c in 1:nc))
    @constraint(model, [k = 1:2], winning[k] + 1 <= winning[k + 1])
    return model, Dict("winning_cards" => winning)
end
