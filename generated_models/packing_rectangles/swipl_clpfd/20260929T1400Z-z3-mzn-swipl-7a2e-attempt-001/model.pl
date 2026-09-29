:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Rectangle packing: place rectangles of given widths and heights, without
% overlap and without rotation, inside the smallest possible enclosing rectangle
% (smallest area). Positions start at 0.
model(Instance, Vars, [pos_x-Xs, pos_y-Ys, total_x-TotalX, total_y-TotalY], min(Area)) :-
    Widths = Instance.widths,
    Heights = Instance.heights,
    length(Widths, N),
    max_list(Widths, WidestItem), sum_list(Widths, SumWidths),
    max_list(Heights, TallestItem), sum_list(Heights, SumHeights),

    % the enclosing rectangle is at least as wide / high as the widest / tallest
    % item and never needs to exceed placing all items side by side / on top of each other
    TotalX in WidestItem..SumWidths,
    TotalY in TallestItem..SumHeights,

    % Xs[i], Ys[i] = lower-left corner of item i
    length(Xs, N), Xs ins 0..SumWidths,
    length(Ys, N), Ys ins 0..SumHeights,

    % every item lies completely inside the enclosing rectangle
    maplist({TotalX}/[X, W]>>(X + W #=< TotalX), Xs, Widths),
    maplist({TotalY}/[Y, H]>>(Y + H #=< TotalY), Ys, Heights),

    % no two items overlap
    rectangles(Xs, Widths, Ys, Heights, Rectangles),
    disjoint2(Rectangles),

    % the area of the enclosing rectangle, to be minimised
    Area #= TotalX * TotalY,
    append([Xs, Ys, [TotalX, TotalY, Area]], Vars).

% rectangles(+Xs, +Widths, +Ys, +Heights, -Rectangles): the f(X, W, Y, H) terms disjoint2/1 expects
rectangles([], [], [], [], []).
rectangles([X|Xs], [W|Ws], [Y|Ys], [H|Hs], [f(X, W, Y, H)|Rectangles]) :-
    rectangles(Xs, Ws, Ys, Hs, Rectangles).
