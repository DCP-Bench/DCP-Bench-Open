:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Big Bang non-transitive dice: five dice with six faces each, face values 1 to
% 12, such that the "beats" relation between the dice follows the game
% Rock-Paper-Scissors-Lizard-Spock. Die A beats die B when A shows the larger
% face in more than half of all pairs of faces.
model(_Instance, Vars, [dice-Dice]) :-
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

    % How many faces of a die show each value. Counts[d][v-1] is the number of
    % faces of die d showing v, and Below[d][v-1] the number of faces of die d
    % showing less than v. They follow from the faces and let the search decide
    % the dice by their counts, so that dice with the same faces in another
    % order are not tried again.
    maplist({MaxFace}/[Die, Counts]>>face_counts(Die, MaxFace, Counts), Dice, CountLists),
    maplist(faces_below, CountLists, BelowLists),

    % The winner of each rule shows the larger face in more than half of all
    % NumFaces * NumFaces pairs of faces. A face of the winner showing v beats
    % Below[loser][v-1] faces of the loser, so the pairs won add up over the
    % faces of the winner. Using the faces here (rather than a sum over the
    % values) lets the search bound the pairs won by the best value each face
    % can still take.
    Half is (NumFaces * NumFaces) // 2,
    maplist({Dice, BelowLists, Half}/[[Winner, Loser]]>>
                (nth0(Winner, Dice, WinnerFaces),
                 nth0(Loser, BelowLists, LoserBelow),
                 maplist({LoserBelow}/[Face, FacesBeaten]>>element(Face, LoserBelow, FacesBeaten),
                         WinnerFaces, Beaten),
                 sum(Beaten, #>, Half)),
            Beats),

    % The search first decides how many faces of each die show each value, then
    % which face shows what (the counts leave only the order of the faces open).
    append(CountLists, Counts),
    append(Dice, Faces),
    append(Counts, Faces, Vars),
    % diagnostic
    statistics(cputime, Built),
    format(user_error, "BUILD ~w~n", [Built]),
    CountLists = [D0, D1, D2|_],
    when(ground(D0), (statistics(cputime, T0), format(user_error, "D0 ~w at ~w~n", [D0, T0]))),
    when(ground(D0-D1), (statistics(cputime, T1), format(user_error, "D0 ~w D1 ~w at ~w~n", [D0, D1, T1]))),
    when(ground(D0-D1-D2), (statistics(cputime, T2), format(user_error, "D0 ~w D1 ~w D2 ~w at ~w~n", [D0, D1, D2, T2]))).


% face_counts(+Die, +MaxFace, -Counts): Counts[v-1] is the number of faces of Die
% that show the value v, for v = 1..MaxFace.
face_counts(Die, MaxFace, Counts) :-
    numlist(1, MaxFace, Values),
    length(Counts, MaxFace),
    pairs_keys_values(Pairs, Values, Counts),
    global_cardinality(Die, Pairs).

% faces_below(+Counts, -Below): Below[v-1] is the number of faces showing less
% than v, the sum of the counts before position v.
faces_below(Counts, Below) :-
    faces_below(Counts, 0, Below).

faces_below([], _, []).
faces_below([Count|Counts], Smaller, [Smaller|Below]) :-
    Smaller1 #= Smaller + Count,
    faces_below(Counts, Smaller1, Below).
