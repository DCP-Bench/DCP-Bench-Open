% Big Bang non-transitive dice: five dice with six faces each (face values 1..12,
% values may repeat) such that their "beats" relations match the game Rock,
% Paper, Scissors, Lizard, Spock: every choice beats two others and loses to
% two others. Die A beats die B if A's face is strictly larger than B's face
% in more than half of all pairs of faces. This problem has no instance data:
% the number of dice and faces and the beats relation are fixed by the problem statement.
include "globals.mzn";

int: m = 5;   % number of dice
int: n = 6;   % faces of each die
int: f = 12;  % largest face value

% the dice, in the order they appear in the output
int: rock = 0; int: paper = 1; int: scissors = 2; int: lizard = 3; int: spock = 4;

% beats[k, 1] beats beats[k, 2] (the ten relations of the game, fixed by the problem statement)
int: n_beats = 10;
array[1..n_beats, 1..2] of int: beats = array2d(1..n_beats, 1..2, [
    rock, scissors,      % Rock crushes Scissors
    rock, lizard,        % Rock crushes Lizard
    paper, rock,         % Paper covers Rock
    paper, spock,        % Paper disproves Spock
    scissors, paper,     % Scissors cuts Paper
    scissors, lizard,    % Scissors decapitates Lizard
    lizard, paper,       % Lizard eats Paper
    lizard, spock,       % Lizard poisons Spock
    spock, rock,         % Spock vaporizes Rock
    spock, scissors      % Spock smashes Scissors
]);

% dice[i, j] = value on the j-th face of die i
array[0..m - 1, 1..n] of var 1..f: dice;

% Counting faces by value makes "how many pairs of faces does A win" a sum over
% values instead of over the n*n pairs of faces, which Gecode propagates much
% better than the reified comparison of every pair (the direct form found no
% dice within the time limit). Both arrays below are determined by dice, so they
% add no freedom to the answer.
%   faces_with[i, v] = number of faces of die i that show the value v
%   faces_below[i, v] = number of faces of die i that show a value smaller than v
array[0..m - 1, 1..f] of var 0..n: faces_with;
array[0..m - 1, 1..f] of var 0..n: faces_below;
constraint forall(i in 0..m - 1) (global_cardinality([dice[i, j] | j in 1..n], [v | v in 1..f], [faces_with[i, v] | v in 1..f]));
constraint forall(i in 0..m - 1, v in 1..f) (faces_below[i, v] = sum(w in 1..v - 1) (faces_with[i, w]));

% for every relation "winner beats loser", the number of pairs of faces where the
% winner's face is larger must be more than half of all n*n pairs of faces; the
% faces of the winner showing the value v each beat faces_below[loser, v] faces
constraint forall(k in 1..n_beats)
    (sum(v in 1..f) (faces_with[beats[k, 1], v] * faces_below[beats[k, 2], v]) > (n * n) div 2);

solve satisfy;

output ["{\"dice\": [", join(", ", ["[" ++ join(", ", [show(dice[i, j]) | j in 1..n]) ++ "]" | i in 0..m - 1]), "]}"];
