% Rectangular packing: place n rectangles with widths Ws and heights Hs into a
% larger rectangle of size total_x by total_y without overlap, all rectangles
% inside the larger one, minimising the area total_x * total_y.
% Positions start at 0. Rectangles are not rotated (the statement does not allow it).

:- lib(ic).

model(Instance, Vars, Outputs, min(Cost)) :-
    memberchk(widths-Ws, Instance),
    memberchk(heights-Hs, Instance),
    length(Ws, N),
    length(Hs, N),
    % the sums of widths and heights bound the container: items placed side by
    % side never need more than their total width or total height
    ( foreach(W, Ws), fromto(0, S0, S1, SumW) do S1 is S0 + W ),
    ( foreach(H, Hs), fromto(0, T0, T1, SumH) do T1 is T0 + H ),
    % the container is at least as wide as the widest item and as tall as the tallest
    ( foreach(W, Ws), fromto(0, M0, M1, MaxW) do M1 is max(M0, W) ),
    ( foreach(H, Hs), fromto(0, K0, K1, MaxH) do K1 is max(K0, H) ),
    % the items together cover at least the sum of their areas
    ( foreach(W, Ws), foreach(H, Hs), fromto(0, A0, A1, AreaSum) do A1 is A0 + W * H ),
    length(Xs, N),
    length(Ys, N),
    Xs :: 0..SumW,
    Ys :: 0..SumH,
    TX :: MaxW..SumW,
    TY :: MaxH..SumH,

    % every item lies within the larger rectangle: its right edge and top edge
    % do not pass total_x and total_y
    ( foreach(X, Xs), foreach(W, Ws), param(TX) do X + W #=< TX ),
    ( foreach(Y, Ys), foreach(H, Hs), param(TY) do Y + H #=< TY ),

    % no two items overlap: for each pair, one lies left of the other, or one lies
    % below the other
    ( foreach(X, Xs), foreach(Y, Ys), foreach(W, Ws), foreach(H, Hs),
      foreach(item(X, Y, W, H), Items) do true ),
    no_overlap(Items),

    % the objective: minimise the area of the larger rectangle, which is at least
    % the total area of the items
    Cost #= TX * TY,
    Cost #>= AreaSum,

    append(Xs, Ys, XY),
    Vars = [TX, TY | XY],
    Outputs = [pos_x-Xs, pos_y-Ys, total_x-TX, total_y-TY].

no_overlap([]).
no_overlap([item(X1, Y1, W1, H1) | Rest]) :-
    ( foreach(item(X2, Y2, W2, H2), Rest), param(X1, Y1, W1, H1) do
        ( (X1 + W1 #=< X2) or (X2 + W2 #=< X1) or
          (Y1 + H1 #=< Y2) or (Y2 + H2 #=< Y1) )
    ),
    no_overlap(Rest).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
