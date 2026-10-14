:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Balanced incomplete block design: arrange v objects into b blocks so that a
% block holds k objects, an object lies in r blocks, and any two distinct
% objects share exactly l blocks. Solved through the v x b incidence matrix.
model(Instance, Vars, [matrix-Rows]) :-
    V = Instance.v,
    B = Instance.b,
    R = Instance.r,
    K = Instance.k,
    L = Instance.l,

    % Rows[i][j] is 1 when object i belongs to block j
    length(Rows, V),
    maplist({B}/[Row]>>(length(Row, B), Row ins 0..1), Rows),

    % every object occurs in exactly r blocks (each row adds up to r)
    maplist({R}/[Row]>>sum(Row, #=, R), Rows),
    % every block contains exactly k objects (each column adds up to k)
    transpose(Rows, Columns),
    maplist({K}/[Column]>>sum(Column, #=, K), Columns),

    % any two distinct objects occur together in exactly l blocks: the scalar
    % product of their rows is l
    findall(I-J, (between(1, V, I), I1 is I + 1, between(I1, V, J)), Pairs),
    maplist({Rows, L}/[I-J]>>(nth1(I, Rows, RowI), nth1(J, Rows, RowJ),
                              maplist([X, Y, P]>>(P #= X * Y), RowI, RowJ, Products),
                              sum(Products, #=, L)), Pairs),
    append(Rows, Vars).
