include "globals.mzn";

% Constants for features
int: ONE = 1; int: TWO = 2; int: THREE = 3;
int: RED = 1; int: PURPLE = 2; int: GREEN = 3;
int: DIAMOND = 1; int: RECT = 2; int: ELLIPSE = 3;
int: FULL = 1; int: EMPTY = 2; int: STRIPED = 3;

% Number of cards in the input deck
int: num_cards = 12;

% Cards data: each card is an array of 4 features: number, fill, color, shape
array[1..num_cards, 1..4] of int: cards_data = [
    [ONE, EMPTY, GREEN, DIAMOND],
    [TWO, STRIPED, RED, RECT],
    [THREE, STRIPED, GREEN, DIAMOND],
    [THREE, FULL, RED, DIAMOND],
    [ONE, STRIPED, GREEN, DIAMOND],
    [ONE, EMPTY, RED, DIAMOND],
    [TWO, FULL, PURPLE, DIAMOND],
    [THREE, FULL, PURPLE, ELLIPSE],
    [THREE, FULL, GREEN, RECT],
    [ONE, FULL, PURPLE, DIAMOND],
    [ONE, STRIPED, PURPLE, DIAMOND],
    [ONE, FULL, GREEN, RECT]
];

% Decision variables: indices of the three cards forming the winning set
array[1..3] of var 1..num_cards: winning_cards;

% Ensure the three cards are distinct
constraint alldifferent(winning_cards);

% Extract features of the chosen cards for convenience
array[1..3, 1..4] of var int: chosen_features = 
  array2d(1..3, 1..4, [cards_data[winning_cards[i], f] | i in 1..3, f in 1..4]);

% Predicate to check if three values are all same or all different
predicate all_same_or_all_diff(var int: a, var int: b, var int: c) =
    (a == b /\ b == c) \/ (a != b /\ b != c /\ a != c);

% For each feature (number, fill, color, shape), the three cards must be all same or all different
constraint forall(f in 1..4) (
    all_same_or_all_diff(chosen_features[1,f], chosen_features[2,f], chosen_features[3,f])
);

solve satisfy;

output [
    "{",
    "\"winning_cards\": ", show(winning_cards),
    "}"
];