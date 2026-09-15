:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Three coins: flip exactly one coin per move and finish with every coin
% showing the same face.
model(Instance, Vars, [steps-Rows]) :-
    NumMoves = Instance.num_moves,
    Init = Instance.init,
    length(Init, N),
    Length is NumMoves + 1,
    length(Rows, Length),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows),
    append(Rows, Vars),
    Rows = [First|_],
    maplist([Coin, Start]>>(Coin #= Start), First, Init),
    one_flip_per_move(Rows),
    % The final row is all heads or all tails.
    last(Rows, Final),
    sum(Final, #=, LastVal),
    (LastVal #= 0 #\/ LastVal #= N).

one_flip_per_move([_]).
one_flip_per_move([Before, After|Rest]) :-
    maplist([B, A, Differs]>>(B #\= A #<==> Differs), Before, After, Changes),
    sum(Changes, #=, 1),
    one_flip_per_move([After|Rest]).
