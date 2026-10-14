:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% People in a room: 13 people, 4 of them male, enter a room one at a time. Find
% an order of males and females so that at every moment the ratio of females
% to males in the room is at most 7/3. The problem has no instance data; the
% 13 people, the 4 males and the ratio 7/3 are the ones in the statement.
% Sequence[i] is 0 if the i-th person to enter is male and 1 if female.
model(_Instance, Vars, [sequence-Sequence]) :-
    TotalPeople = 13,
    NumMales = 4,

    length(Sequence, TotalPeople),
    Vars = Sequence,
    Vars ins 0..1,

    % exactly 4 of the 13 are male, so the other 9 are female
    NumFemales is TotalPeople - NumMales,
    sum(Sequence, #=, NumFemales),

    % after each of the first 12 people has entered, females : males is at most
    % 7 : 3, i.e. 3 * females <= 7 * males (as in the reference, the check after
    % all 13 have entered is left out; the totals 9 and 4 already satisfy it)
    Checks is TotalPeople - 1,
    numlist(1, Checks, Prefixes),
    maplist(ratio_holds(Sequence), Prefixes).

% ratio_holds(+Sequence, +I): among the first I people to enter, 3 times the
% number of females is at most 7 times the number of males.
ratio_holds(Sequence, I) :-
    length(Prefix, I),
    append(Prefix, _, Sequence),
    sum(Prefix, #=, Females),
    Males #= I - Females,
    3 * Females #=< 7 * Males.
