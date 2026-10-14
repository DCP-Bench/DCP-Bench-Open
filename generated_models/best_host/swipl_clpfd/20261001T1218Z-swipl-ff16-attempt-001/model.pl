:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Best host: six guests sit around a table. Each guest only gets along with two
% of the others and must sit between guests they get along with. Find the
% seating order. The guests, numbered 0..5 as in the problem, are Andrew (0),
% Betty (1), Cara (2), Dave (3), Erica (4) and Frank (5).
model(_Instance, Seating, [x-Seating]) :-
    % This table belongs to the problem, not to an instance (there are no
    % instance fields): Prefs[g] lists the two guests that guest g will sit
    % next to. Andrew: Dave, Frank. Betty: Cara, Erica. Cara: Betty, Frank.
    % Dave: Andrew, Erica. Erica: Betty, Dave. Frank: Andrew, Cara.
    Prefs = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]],
    length(Prefs, N),
    Last is N - 1,

    % Seating[i] is the guest in seat i; the seats go around the table.
    length(Seating, N),
    Seating ins 0..Last,
    % every guest has one seat
    all_distinct(Seating),

    % [guest, neighbour] pairs that get along
    findall([Guest, Neighbour],
            (nth0(Guest, Prefs, Row), member(Neighbour, Row)),
            GetAlong),

    % every guest sits between guests they get along with: of two guests in
    % neighbouring seats (the last seat is next to the first), each is among
    % the other's preferred neighbours
    Seating = [First|_],
    append(Seating, [First], Circle),
    next_to_each_other(Circle, GetAlong).

% next_to_each_other(+Seats, +GetAlong): every two guests in neighbouring seats
% of the list get along, in both directions.
next_to_each_other([_], _) :- !.
next_to_each_other([Left, Right|Rest], GetAlong) :-
    tuples_in([[Left, Right], [Right, Left]], GetAlong),
    next_to_each_other([Right|Rest], GetAlong).
