% The card game Set: among the cards on the table find three that form a set,
% that is, for each of the four features (number, fill, colour, shape) the three
% cards either all show the same value or all show different values.
include "globals.mzn";

array[int, int] of int: cards_data;  % each card is [number, fill, colour, shape]
int: n_cards = card(index_set_1of2(cards_data));

% winning_cards = the indices of the three chosen cards, counted from 0 as in the
% answer (card i is row i + 1 of the data), all different
array[1..3] of var 0..n_cards - 1: winning_cards;
constraint all_different(winning_cards);

% for each feature, the three chosen cards show all the same value or all different values
constraint forall(f in 1..4) (
    let { var int: a = cards_data[winning_cards[1] + 1, f];
          var int: b = cards_data[winning_cards[2] + 1, f];
          var int: c = cards_data[winning_cards[3] + 1, f] } in
    ((a = b /\ b = c) \/ all_different([a, b, c])));

solve satisfy;

output ["{\"winning_cards\": [", join(", ", [show(winning_cards[k]) | k in 1..3]), "]}"];
