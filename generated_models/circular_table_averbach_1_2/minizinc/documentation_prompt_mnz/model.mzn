% We have three players: X, Y, Z
% Three nationalities: American, English, French
% Each player has a unique nationality, so these are permutations of {0,1,2}

include "globals.mzn";

% Define the domain for players and nationalities
set of int: Players = 0..2; % 0=X, 1=Y, 2=Z
set of int: Nationalities = 0..2; % 0=American, 1=English, 2=French

% Decision variables: nationality assigned to each player
array[Players] of var Nationalities: nationality;

% Decision variables: player assigned to each nationality (inverse)
array[Nationalities] of var Players: player_of;

% Inverse relation between nationality and player
constraint inverse(nationality, player_of);

% The players are seated around a circular table: X(0), Y(1), Z(2)
% Passing cards to the person on their right:
% The right of player i is (i-1) mod 3
function int: right_of(int: i) = if i == 0 then 2 else i - 1 endif;

% Given facts:
% 1) Y passed three hearts to the American
%    => The player to the right of Y is the American
%    => right_of(Y) = American
%    Y is player 1
constraint nationality[right_of(1)] = nationality[1]; % This would mean Y passed to Y, which is impossible
% Wait, we need to be careful:
% Y passed three hearts to the American
% So the person to the right of Y is the American
% The person to the right of Y is right_of(1) = 0 (X)
% So nationality of X = American
constraint nationality[0] = 0; % X is American

% 2) X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman.
% Let's analyze this carefully:
% - X passed cards to right_of(X) = right_of(0) = 2 (Z)
% - The person who passed their cards to the Frenchwoman is the person who passed cards to nationality=French
%   The Frenchwoman is nationality=2
%   The person who passed cards to Frenchwoman is the player to the left of the Frenchwoman (since passing is to the right)
%   Because passing is to the right, the person who passed cards to Frenchwoman is left_of(Frenchwoman)
%   left_of(i) = (i+1) mod 3
% So:
% Let f = player_of[2] (player who is Frenchwoman)
% The person who passed cards to Frenchwoman is left_of(f) = (f+1) mod 3
% X passed cards to Z
% The person who passed cards to Frenchwoman is left_of(f)
% So Z = left_of(f)
% So Z = (f+1) mod 3
% Also, X passed queen of spades and two diamonds to that person (Z)
% So Z = left_of(f)
constraint right_of(0) = (player_of[2] + 1) mod 3;

% We have nationality[0] = 0 (X is American)
% nationality is a permutation of {0,1,2}
constraint alldifferent(nationality);

% Output variables as required:
% x, y, z: nationality of X, Y, Z respectively
% american, english, french: player assigned to each nationality
% We already have nationality and player_of arrays

solve satisfy;

output [
    "{",
    join(",", [
        "\"x\": " ++ show(nationality[0]),
        "\"y\": " ++ show(nationality[1]),
        "\"z\": " ++ show(nationality[2]),
        "\"american\": " ++ show(player_of[0]),
        "\"english\": " ++ show(player_of[1]),
        "\"french\": " ++ show(player_of[2])
    ]),
    "}"
];