:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).

% Big Bang non-transitive dice: five dice with six faces each, face values 1 to
% 12, such that the "beats" relation between the dice follows the game
% Rock-Paper-Scissors-Lizard-Spock. Die A beats die B when A shows the larger
% face in more than half of all pairs of faces.

% Search: decide the dice one at a time, first how far the sum of its faces
% lies from 39 (the sum of six faces numbered 1..12 on average), closest
% first, then how many faces show each value, value 1 first and the most faces
% first, so the dice of one face sum are tried in the lexicographic order of
% their sorted faces; then place the faces. Nothing is restricted by this: the
% face sum is only labelled, and the face order of a die is left free, so
% every arrangement of a die's faces is still a solution.
labeling_options([leftmost, down, step]).

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

    % Dice[d][f] is the value on face f of die d, 1..12
    length(Dice, NumDice),
    maplist(die(NumFaces, MaxFace), Dice),

    % Counts[d][v-1] is the number of faces of die d showing v, and
    % Below[d][v-1] the number of faces of die d showing less than v. They
    % follow from the faces.
    maplist(face_counts(MaxFace), Dice, CountLists),
    maplist(faces_below, CountLists, BelowLists),

    % The winner of each rule shows the larger face in more than half of all
    % NumFaces * NumFaces pairs of faces: a face of the winner showing v beats
    % the Below[loser][v-1] faces of the loser that show less, so the pairs won
    % are the sum over v of Counts[winner][v-1] * Below[loser][v-1]. Once the
    % search has fixed one die of a rule, that sum is linear in the other.
    Half is (NumFaces * NumFaces) // 2,
    maplist(beats(CountLists, BelowLists, Half), Beats),

    % Closeness[d] = 33 - |sum of the faces of die d - 39|: 33 is the largest
    % distance a sum of six faces in 1..12 can have from 39 (6 or 72). It is
    % labelled from the largest value down, so dice whose faces add up to 39
    % come first. A depth-first search over whole dice (all 12376 multisets of
    % six faces) in this order meets a solution within the first few dice,
    % against about 30000 dice in plain sorted-face order.
    MeanSum is NumFaces * (1 + MaxFace) // 2,
    MaxDistance is max(MeanSum - NumFaces, NumFaces * MaxFace - MeanSum),
    maplist(closeness(MeanSum, MaxDistance, NumFaces), CountLists, Closeness),

    % The dice are decided in the order Rock, Scissors, Paper, Lizard, Spock.
    maplist(die_decisions(Closeness, CountLists), [0, 2, 1, 3, 4], Decisions),
    append(Decisions, Decided),
    % Diagnostics on standard error: when each die in the search order is
    % decided, and how far the search has got.
    nb_setval(decided, 0),
    Decisions = [D1, D2, D3, D4, D5],
    when(ground(D1), report(1, D1)),
    when(ground(D1-D2), report(2, D2)),
    when(ground(D1-D2-D3), report(3, D3)),
    when(ground(D1-D2-D3-D4), report(4, D4)),
    when(ground(D1-D2-D3-D4-D5), report(5, D5)),
    append(Dice, Faces),
    append(Decided, Faces, Vars).

% The face sum is stated over the counts (sum of v * Counts[v-1]), and the
% counts are stated to add up to the number of faces, so that both prune while
% the counts are being decided rather than only once the faces are placed.
closeness(MeanSum, MaxDistance, NumFaces, Counts, Closeness) :-
    length(Counts, MaxFace),
    numlist(1, MaxFace, Values),
    sum(Counts, #=, NumFaces),
    scalar_product(Values, Counts, #=, Sum),
    Closeness in 0..MaxDistance,
    Closeness #= MaxDistance - abs(Sum - MeanSum).

die_decisions(Closeness, CountLists, D, [C|Counts]) :-
    nth0(D, Closeness, C),
    nth0(D, CountLists, Counts).

report(Level, Decision) :-
    nb_getval(decided, N0), N is N0 + 1, nb_setval(decided, N),
    (   ( Level =< 2 ; N mod 200 =:= 0 ; Level >= 4 )
    ->  statistics(cputime, T),
        format(user_error, "L~w ~w n=~w t=~2f~n", [Level, Decision, N, T])
    ;   true
    ).

die(NumFaces, MaxFace, Die) :-
    length(Die, NumFaces),
    Die ins 1..MaxFace.

% face_counts(+MaxFace, +Die, -Counts): Counts[v-1] is the number of faces of
% Die that show the value v, for v = 1..MaxFace.
face_counts(MaxFace, Die, Counts) :-
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

beats(CountLists, BelowLists, Half, [Winner, Loser]) :-
    nth0(Winner, CountLists, WinnerCounts),
    nth0(Loser, BelowLists, LoserBelow),
    maplist(pairs_won, WinnerCounts, LoserBelow, WinsPerValue),
    sum(WinsPerValue, #>, Half).

pairs_won(Count, Below, Wins) :- Wins #= Count * Below.
