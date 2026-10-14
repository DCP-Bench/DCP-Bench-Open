% Big Bang non-transitive dice: five dice with six faces each (face values 1..12,
% values may repeat) such that their "beats" relations match the game Rock,
% Paper, Scissors, Lizard, Spock: every choice beats two others and loses to
% two others. Die A beats die B if A's face is strictly larger than B's face
% in more than half of all pairs of faces. This problem has no instance data:
% the number of dice and faces and the beats relation are fixed by the problem statement.

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

% for every relation "winner beats loser", the number of pairs of faces where the
% winner's face is larger must be more than half of all n*n pairs of faces
constraint forall(k in 1..n_beats)
    (sum(x in 1..n, y in 1..n) (bool2int(dice[beats[k, 1], x] > dice[beats[k, 2], y])) > (n * n) div 2);

solve satisfy;

output ["{\"dice\": [", join(", ", ["[" ++ join(", ", [show(dice[i, j]) | j in 1..n]) ++ "]" | i in 0..m - 1]), "]}"];
