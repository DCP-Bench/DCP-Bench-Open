% Golomb rulers (CSPLib 006): place m marks 0 = a_1 < a_2 < ... < a_m so that
% all m(m-1)/2 pairwise differences are distinct; minimise the length a_m.
% Outputs: length (a_m) and marks (the list a_1..a_m).

:- lib(ic).

model(Instance, Marks, [length-Len, marks-Marks], min(Len)) :-
    memberchk(size-N, Instance),
    % the ruler length is at most N*N for every size in the data
    Max is N * N,
    length(Marks, N),
    Marks :: 0..Max,
    % the first mark is at position 0
    Marks = [0|_],
    % the marks are strictly increasing
    increasing(Marks),
    final_element(Marks, Len),
    % all differences between pairs of marks are distinct
    differences(Marks, Diffs),
    all_different_pairs(Diffs).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% the last element of a list
final_element([X], X).
final_element([_|T], X) :-
    final_element(T, X).

% the marks are strictly increasing
increasing([_]).
increasing([A, B|Rest]) :-
    A #< B,
    increasing([B|Rest]).

% every pairwise difference a_j - a_i with i < j
differences([], []).
differences([X|Xs], Ds) :-
    diffs_from(X, Xs, D1),
    differences(Xs, D2),
    append(D1, D2, Ds).

diffs_from(_, [], []).
diffs_from(X, [Y|Ys], [D|Ds]) :-
    D #= Y - X,
    diffs_from(X, Ys, Ds).

% the differences are all distinct
all_different_pairs([]).
all_different_pairs([D|Ds]) :-
    distinct_from(D, Ds),
    all_different_pairs(Ds).

distinct_from(_, []).
distinct_from(D, [E|Es]) :-
    D #\= E,
    distinct_from(D, Es).
