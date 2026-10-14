:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Giant cat army riddle: start from [0] and extend the list by adding 5, adding
% 7 or taking a square root, so that all numbers are different integers of at
% most 60, the list contains 2, then 10, then 14 (in that order), and it ends
% with 14 after exactly 24 numbers.
%
% The riddle fixes these numbers, so they are mirrored here.
max_value(60).  % largest number allowed in the list
length_of_list(24).  % number of entries in the list
goal(14).  % the last entry

model(_Instance, X, [x-X]) :-
    max_value(Max),
    length_of_list(Length),
    goal(Goal),

    % X[i] = the i-th number of the list
    length(X, Length),
    X ins 0..Max,

    % all numbers are different
    all_distinct(X),

    % the list starts with 0 and ends with 14
    X = [0|_],
    last(X, Goal),

    % each number follows the previous one by adding 5, adding 7, or taking the
    % square root (the previous number is the square of the next one)
    steps(X),

    % the list contains 2 and later 10 (and, as it ends with it, 14 after both);
    % element/3 counts from 1
    element(IndexOf2, X, 2),
    element(IndexOf10, X, 10),
    IndexOf2 #< IndexOf10.

steps([_]).
steps([A, B|Rest]) :-
    (B #= A + 5) #\/ (B #= A + 7) #\/ (A #= B * B),
    steps([B|Rest]).
