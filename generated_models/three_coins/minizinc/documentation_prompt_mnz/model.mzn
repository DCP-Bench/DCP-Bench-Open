include "globals.mzn";

int: num_moves = 3;  % Number of moves to make all coins face either all heads or all tails
array[1..3] of int: init = [1, 0, 1];  % Initial configuration of the coins (1=heads, 0=tails)

% We represent the coins as 0 (tails) or 1 (heads)
% Each move flips exactly one coin (0->1 or 1->0)
% We want to find a sequence of moves (steps) that leads to all heads or all tails after num_moves moves

% Decision variables: steps[i] is the index of the coin flipped at move i (1-based)
array[1..num_moves] of var 1..3: steps;

% State of coins after each move: coins_state[m] is the configuration after m moves
array[0..num_moves, 1..3] of var 0..1: coins_state;

% Initial state
constraint forall(c in 1..3) (coins_state[0,c] = init[c]);

% State transitions: flipping the coin at steps[m]
constraint forall(m in 1..num_moves, c in 1..3) (
    coins_state[m,c] = if c = steps[m] then 1 - coins_state[m-1,c] else coins_state[m-1,c]
);

% Final state must be all heads (1) or all tails (0)
constraint
    (forall(c in 1..3) (coins_state[num_moves,c] = 0)) \/
    (forall(c in 1..3) (coins_state[num_moves,c] = 1));

solve satisfy;

output [
    "{",
    "\"steps\": ", show(steps),
    "}"
];