% Include necessary library
include "globals.mzn";

% Decision variables: quantities of each fruit
var 0..100: bananas;
var 0..100: oranges;
var 0..100: mangoes;
var 0..100: apples;

% Constraints
constraint bananas + oranges + mangoes + apples == 100; % total fruits
constraint 3 * bananas + 5 * oranges + 7 * mangoes + 9 * apples == 100; % total cost

% All types of fruits need to be purchased
constraint bananas >= 1;
constraint oranges >= 1;
constraint mangoes >= 1;
constraint apples >= 1;

% Minimize bananas and apples since user dislikes them
% We minimize the sum of bananas and apples
solve minimize bananas + apples;

output [
    "{",
    "\"bananas\": ", show(bananas), ",",
    "\"oranges\": ", show(oranges), ",",
    "\"mangoes\": ", show(mangoes), ",",
    "\"apples\": ", show(apples),
    "}"
];