include "globals.mzn";

% Number of dice and faces per die
int: num_dice = 5;
int: faces = 6;

% Dice indices for readability
enum DICE = {Rock, Paper, Scissors, Lizard, Spock};

% Decision variables: dice values, each die has 6 faces with values 1..30
array[DICE, 1..faces] of var 1..30: dice;

% Constraint: all faces in a die are distinct
constraint
  forall(d in DICE) (
    alldifferent([dice[d, f] | f in 1..faces])
  );

% Constraint: all dice faces are distinct across all dice (optional for uniqueness)
% This is not strictly necessary, but helps avoid trivial solutions
constraint
  alldifferent([dice[d, f] | d in DICE, f in 1..faces]);

% The dominance relationships as per the problem statement:
% Each die beats two others, and is beaten by two others.
% We define a predicate to count how many times die A beats die B:
% die A beats die B if a face of A is strictly greater than a face of B.

% Function to count how many pairs (a,b) with a in die A and b in die B satisfy a > b
function var int: count_beats(array[1..faces] of var int: A, array[1..faces] of var int: B) =
  sum([bool2int(A[i] > B[j]) | i,j in 1..faces]);

% For each dominance relation, the first die must beat the second die more than half the pairs (i.e. > 18)
% since total pairs = 6*6=36, majority is >18

% Define the beats constraints according to the 10 relationships:
constraint count_beats(dice[Rock], dice[Scissors]) > 18;   % 1: Rock crushes Scissors
constraint count_beats(dice[Rock], dice[Lizard]) > 18;     % 2: Rock crushes Lizard
constraint count_beats(dice[Paper], dice[Rock]) > 18;      % 3: Paper covers Rock
constraint count_beats(dice[Paper], dice[Spock]) > 18;     % 4: Paper disproves Spock
constraint count_beats(dice[Scissors], dice[Paper]) > 18;  % 5: Scissors cuts Paper
constraint count_beats(dice[Scissors], dice[Lizard]) > 18; % 6: Scissors decapitates Lizard
constraint count_beats(dice[Lizard], dice[Paper]) > 18;    % 7: Lizard eats Paper
constraint count_beats(dice[Lizard], dice[Spock]) > 18;    % 8: Lizard poisons Spock
constraint count_beats(dice[Spock], dice[Rock]) > 18;      % 9: Spock vaporizes Rock
constraint count_beats(dice[Spock], dice[Scissors]) > 18;  % 10: Spock smashes Scissors

% To avoid trivial solutions, enforce ordering of dice faces within each die
constraint
  forall(d in DICE) (
    forall(f in 1..faces-1) (
      dice[d,f] < dice[d,f+1]
    )
  );

solve satisfy;

output [
  "{",
  "\"dice\": [",
  join(",\n", [
    "[" ++ join(", ", [show(dice[d,f]) | f in 1..faces]) ++ "]"
    | d in DICE
  ]),
  "]",
  "}"
];