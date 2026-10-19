% Three coins: three coins lie on a table in the order tails, heads, tails.
% In precisely three moves make them face either all heads or all tails.
% Each move consists of choosing one coin and flipping it over.
% steps[t][i] is 1 for tails and 0 for heads: row t is the state after t moves.
:- lib(ic).
:- lib(lists).

model(Instance, Vars, [steps-Rows]) :-
    memberchk(init-Init, Instance),
    memberchk(num_moves-M, Instance),
    length(Init, C),
    T is M + 1,
    length(Rows, T),
    ( foreach(Row, Rows), param(C) do
        length(Row, C),
        Row :: 0..1
    ),
    % the first state is the initial configuration
    Rows = [Init | _],
    % each move consists of choosing one coin and flipping it over
    moves(Rows),
    % in precisely three moves make them face either all heads or all tails
    last_row(Rows, Last),
    Last = [F | Rest],
    ( foreach(X, Rest), param(F) do
        X #= F
    ),
    flatten(Rows, Vars).

% consecutive states differ by exactly one flipped coin
moves([_]).
moves([A, B | Rest]) :-
    one_flip(A, B),
    moves([B | Rest]).

one_flip(A, B) :-
    ( foreach(X, A), foreach(Y, B), foreach(D, Ds) do
        D #= abs(X - Y)
    ),
    Ds :: 0..1,
    sum(Ds) #= 1.

last_row([R], R).
last_row([_ | T], R) :-
    last_row(T, R).
