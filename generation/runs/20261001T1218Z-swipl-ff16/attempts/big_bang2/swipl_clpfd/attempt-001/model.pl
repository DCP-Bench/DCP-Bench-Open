:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Big Bang non-transitive dice: five dice with six faces each, face values 1 to
% 12, such that the "beats" relation between the dice follows the game
% Rock-Paper-Scissors-Lizard-Spock. Die A beats die B when A shows the larger
% face in more than half of all pairs of faces.
model(_Instance, Faces, [dice-Dice]) :-
    % The numbers of dice and faces, the largest face value and the ten
    % "beats" rules belong to the problem (there are no instance fields).
    % Dice: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock; each pair is
    % [winner, loser].
    NumDice = 5,
    NumFaces = 6,
    MaxFace = 12,
    Beats = [[0, 2],    % Rock crushes Scissors
             [0, 3],    % Rock crushes Lizard
             [1, 0],    % Paper covers Rock
             [1, 4],    % Paper disproves Spock
             [2, 1],    % Scissors cuts Paper
             [2, 3],    % Scissors decapitates Lizard
             [3, 1],    % Lizard eats Paper
             [3, 4],    % Lizard poisons Spock
             [4, 0],    % Spock vaporizes Rock
             [4, 2]],   % Spock smashes Scissors

    % Dice[d][f] is the value on face f of die d.
    length(Dice, NumDice),
    maplist({NumFaces, MaxFace}/[Die]>>(length(Die, NumFaces), Die ins 1..MaxFace), Dice),
    append(Dice, Faces),

    % the winner of each rule shows the larger face in more than half of all
    % NumFaces * NumFaces pairs of faces
    Half is (NumFaces * NumFaces) // 2,
    maplist({Dice, Half}/[[Winner, Loser]]>>
                (nth0(Winner, Dice, WinnerFaces),
                 nth0(Loser, Dice, LoserFaces),
                 pairs_won(WinnerFaces, LoserFaces, Wins),
                 sum(Wins, #>, Half)),
            Beats).

% pairs_won(+Faces1, +Faces2, -Wins): Wins holds a 0/1 variable for every pair of
% a face of Faces1 and a face of Faces2, 1 when the first is larger.
pairs_won(Faces1, Faces2, Wins) :-
    maplist({Faces2}/[X, Row]>>maplist({X}/[Y, Win]>>(Win #<==> (X #> Y)), Faces2, Row),
            Faces1, Rows),
    append(Rows, Wins).
