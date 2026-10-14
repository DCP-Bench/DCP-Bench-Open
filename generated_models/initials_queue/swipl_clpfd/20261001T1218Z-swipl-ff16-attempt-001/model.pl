:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Initials queue: the first ten people in a queue each have initials that are
% an alphabetically ordered pair of distinct letters from A, B, C, D, E. No two
% people have the same initials and nobody shares a letter with the person in
% front of them. BE is at the front, CD is right behind, and BD is at the end.
% Find the initials of the ten people, from the front. The problem has no
% instance data; the queue length and the three known people are the ones in
% the statement. Letters are coded A=0, B=1, C=2, D=3, E=4, and Queue[i] is
% the pair [first letter, second letter] of person i.
model(_Instance, Vars, [queue-Queue]) :-
    N = 10,
    A = 0, B = 1, C = 2, D = 3, E = 4,

    length(Queue, N),
    maplist(initials_pair, Queue),
    append(Queue, Vars),
    Vars ins A..E,

    % the two letters of each person are in alphabetical order, so they differ
    maplist(alphabetical, Queue),

    % no two people have the same initials
    all_different_initials(Queue),

    % nobody shares a letter with the person in front of them
    no_shared_letter(Queue),

    % BE is at the front, CD is right behind, BD is at the end
    Queue = [[B, E], [C, D]|_],
    last(Queue, [B, D]).

% a person is a pair of letters
initials_pair([_, _]).

alphabetical([First, Second]) :-
    First #< Second.

% two people differ in at least one of the two letters
all_different_initials([]).
all_different_initials([Person|Rest]) :-
    maplist(different_initials(Person), Rest),
    all_different_initials(Rest).

different_initials([X1, Y1], [X2, Y2]) :-
    X1 #\= X2 #\/ Y1 #\= Y2.

% each person shares neither letter with the next one in the queue
no_shared_letter([]).
no_shared_letter([_]).
no_shared_letter([[X1, Y1], [X2, Y2]|Rest]) :-
    X1 #\= X2, X1 #\= Y2,
    Y1 #\= X2, Y1 #\= Y2,
    no_shared_letter([[X2, Y2]|Rest]).
