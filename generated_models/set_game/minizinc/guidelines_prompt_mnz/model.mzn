
% Include necessary global constraints
include "globals.mzn";

% Data: number of cards and features
int: n_cards = 12;
int: n_features = 4;

% cards_data[c, f] = feature f of card c
% Features order: [number, fill, color, shape]
array[1..n_cards, 1..n_features] of int: cards_data = array2d(
  1..n_cards, 1..n_features,
  [
    %  number, fill, color, shape
       1,      2,    3,     1,   % Card 1: [ONE, EMPTY, GREEN, DIAMOND]
       2,      3,    1,     2,   % Card 2: [TWO, STRIPED, RED, RECT]
       3,      3,    3,     1,   % Card 3: [THREE, STRIPED, GREEN, DIAMOND]
       3,      1,    1,     1,   % Card 4: [THREE, FULL, RED, DIAMOND]
       1,      3,    3,     1,   % Card 5: [ONE, STRIPED, GREEN, DIAMOND]
       1,      2,    1,     1,   % Card 6: [ONE, EMPTY, RED, DIAMOND]
       2,      1,    2,     1,   % Card 7: [TWO, FULL, PURPLE, DIAMOND]
       3,      1,    2,     3,   % Card 8: [THREE, FULL, PURPLE, ELLIPSE]
       3,      1,    3,     2,   % Card 9: [THREE, FULL, GREEN, RECT]
       1,      1,    2,     1,   % Card 10: [ONE, FULL, PURPLE, DIAMOND]
       1,      3,    2,     1,   % Card 11: [ONE, STRIPED, PURPLE, DIAMOND]
       1,      1,    3,     2    % Card 12: [ONE, FULL, GREEN, RECT]
  ]
);

% Decision variables: choose three distinct cards
array[1..3] of var 1..n_cards: winning_cards;

% No repeated cards
constraint all_different(winning_cards);

% For each feature, the three selected cards must be all same or all different
constraint
  forall(f in 1..n_features) (
    let {
      var int: v1 = cards_data[winning_cards[1], f],
      var int: v2 = cards_data[winning_cards[2], f],
      var int: v3 = cards_data[winning_cards[3], f]
    } in
      (v1 = v2 /\ v2 = v3)
      \/
      (v1 != v2 /\ v1 != v3 /\ v2 != v3)
  );

solve satisfy;

% Output the indices of the winning set in JSON format
output [
  "{",
  join(",", [
    "\"winning_cards\": [" ++ join(",", [ show(winning_cards[i]) | i in 1..3 ]) ++ "]"
  ]),
  "}"
];
