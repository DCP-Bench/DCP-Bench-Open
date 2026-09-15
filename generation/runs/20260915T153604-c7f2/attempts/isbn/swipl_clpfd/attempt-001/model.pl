:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% ISBN-13: recover the digits marked -1, respecting the 978/979 prefix and the
% weighted check-digit rule.
model(Instance, Isbn, [isbn-Isbn]) :-
    Init = Instance.isbn_init,
    length(Init, N),
    length(Isbn, N),
    Isbn ins 0..9,
    % Anything not marked -1 is already known.
    maplist([D, Known]>>(Known =:= -1 -> true ; D #= Known), Isbn, Init),
    % ISBN-13 prefixes: 978 or 979.  These belong to the numbering scheme
    % rather than the instance, and the reference fixes them the same way.
    Isbn = [First, Second, Third|_],
    First #= 9,
    Second #= 7,
    Third in 8..9,
    % Check digit: 10 minus the weighted sum mod 10, itself taken mod 10 so a
    % remainder of zero gives a check digit of zero rather than ten.
    Body is N - 1,
    length(Weights, Body),
    weights(Weights),
    length(Front, Body),
    append(Front, [Check], Isbn),
    scalar_product(Weights, Front, #=, CheckSum),
    Check #= (10 - (CheckSum mod 10)) mod 10.

% Positions alternate weight 1 and weight 3, starting at 1.
weights(Ws) :- weights(Ws, 0).
weights([], _).
weights([W|Ws], I) :-
    (I mod 2 =:= 0 -> W = 1 ; W = 3),
    Next is I + 1,
    weights(Ws, Next).
