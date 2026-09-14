:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [x_coords-Xs, y_coords-Ys]) :-
    Base = Instance.base,
    Sides = Instance.sides,
    length(Sides, Count),
    length(Xs, Count),
    length(Ys, Count),
    Xs ins 0..Base,
    Ys ins 0..Base,
    maplist({Base}/[X, Side]>>(X + Side #=< Base), Xs, Sides),
    maplist({Base}/[Y, Side]>>(Y + Side #=< Base), Ys, Sides),
    maplist([X, Y, Side, f(X, Side, Y, Side)]>>true, Xs, Ys, Sides, Rectangles),
    disjoint2(Rectangles),
    append(Xs, Ys, Vars).
