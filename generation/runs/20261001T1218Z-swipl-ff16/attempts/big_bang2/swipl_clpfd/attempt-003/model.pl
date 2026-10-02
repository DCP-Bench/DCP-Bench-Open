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

    % How many faces of a die show each value. Counting faces by value lets
    % the number of pairs a die wins be written as a sum over the values
    % instead of over all NumFaces * NumFaces pairs of faces, which propagates
    % much better. Counts[d][v-1] is the number of faces of die d showing v,
    % and Below[d][v-1] the number of faces of die d showing less than v.
    maplist({MaxFace}/[Die, Counts]>>face_counts(Die, MaxFace, Counts), Dice, CountLists),
    maplist(faces_below, CountLists, BelowLists),

    % A die is also picked as a whole: Choices[d] says which of all the ways to
    % spread NumFaces faces over the values (listed once each, in a scrambled
    % order) die d shows. The search tries the choices in that order. Listed
    % by value, the first ways would all be extreme dice that no
    % non-transitive set can contain, and the search would spend its time
    % proving that.
    spreads(NumFaces, MaxFace, Spreads),
    length(Choices, NumDice),
    maplist({Spreads}/[Choice, Counts]>>tuples_in([[Choice|Counts]], Spreads),
            Choices, CountLists),

    % The winner of each rule shows the larger face in more than half of all
    % NumFaces * NumFaces pairs of faces. Each face of the winner showing v
    % beats the faces of the loser that show less than v.
    Half is (NumFaces * NumFaces) // 2,
    maplist({CountLists, BelowLists, Half}/[[Winner, Loser]]>>
                (nth0(Winner, CountLists, WinnerCounts),
                 nth0(Loser, BelowLists, LoserBelow),
                 maplist([Count, Below, Wins]>>(Wins #= Count * Below),
                         WinnerCounts, LoserBelow, WinsPerValue),
                 sum(WinsPerValue, #>, Half)),
            Beats),

    % The search first picks the dice, then which face shows what (the counts
    % leave only the order of the faces open).
    append(Dice, Faces),
    append(Choices, Faces, Vars).

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

% spreads(+NumFaces, +MaxFace, -Table): one row [k, C1, ..., CMaxFace] for every
% way to spread NumFaces faces over the values 1..MaxFace (Ci faces show i),
% numbered k = 1, 2, ... in a scrambled order: the ways are numbered in the
% order they are generated, and sorted by (7919 * number + 1) mod their count
% (a permutation, as 7919 is prime and does not divide the count).
spreads(NumFaces, MaxFace, Table) :-
    findall(Counts, spread(NumFaces, MaxFace, Counts), Ways),
    length(Ways, Total),
    findall(Key-Counts,
            (nth0(Number, Ways, Counts), Key is (7919 * Number + 1) mod Total),
            Keyed),
    keysort(Keyed, Scrambled),
    pairs_values(Scrambled, Ordered),
    findall([Index|Counts], nth1(Index, Ordered, Counts), Table).

% spread(+Faces, +Values, -Counts): Counts spreads Faces faces over Values values.
spread(Faces, 0, []) :-
    Faces =:= 0.
spread(Faces, Values, [Count|Counts]) :-
    Values > 0,
    between(0, Faces, Count),
    Rest is Faces - Count,
    Values1 is Values - 1,
    spread(Rest, Values1, Counts).
