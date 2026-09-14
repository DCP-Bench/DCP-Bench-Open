:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [matrix-Rows]) :-
    get_dict('N', Instance, N),
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows),
    append(Rows, Vars),
    maplist(degree, Rows),
    sum(Vars, #=, Arcs),
    Arcs mod 12 #= 0,
    findall(I-J, (between(1, N, I), between(1, N, J), I =< J), Pairs),
    maplist(undirected(Rows), Pairs),
    findall(Quad, quadruple(N, Quad), Quads),
    maplist(diamond_free(Rows), Quads).

% No isolated vertex, and every degree is a multiple of three.
degree(Row) :-
    sum(Row, #=, Degree),
    Degree #> 0,
    Degree mod 3 #= 0.

% No self loop on the diagonal, and a symmetric matrix off it.
undirected(Rows, I-I) :- !,
    cell(Rows, I, I, Self),
    Self #= 0.
undirected(Rows, I-J) :-
    cell(Rows, I, J, There),
    cell(Rows, J, I, Back),
    There #= Back.

quadruple(N, [A, B, C, D]) :-
    between(1, N, A), Bs is A + 1, between(Bs, N, B),
    Cs is B + 1, between(Cs, N, C), Ds is C + 1, between(Ds, N, D).

% Any four vertices span at most four of their six edges.
diamond_free(Rows, [A, B, C, D]) :-
    cell(Rows, A, B, AB), cell(Rows, A, C, AC), cell(Rows, A, D, AD),
    cell(Rows, B, C, BC), cell(Rows, B, D, BD), cell(Rows, C, D, CD),
    AB + AC + AD + BC + BD + CD #=< 4.

cell(Rows, I, J, Cell) :-
    nth1(I, Rows, Row),
    nth1(J, Row, Cell).
