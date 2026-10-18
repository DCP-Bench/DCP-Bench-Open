% Vessel loading (CSPLib prob008): place the containers on a rectangular deck,
% without overlapping, and respecting the minimum separations between classes.
% Containers are cuboid, laid out in a single layer, and may be rotated by 90 degrees
% so that they stay parallel to the sides of the deck.
% Outputs: left, right, top, bottom. Container k occupies x in [left, right) and
% y in [bottom, top), with bottom = top - y_extent (top is the high edge).
% A redundant cell-owner view (which container covers each deck cell) is posted.
% When the containers fill the deck exactly, the owner cells are labelled first.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, Outputs) :-
    memberchk(deck_width-DW, Instance),
    memberchk(deck_length-DL, Instance),
    memberchk(n_containers-N, Instance),
    memberchk(width-Ws, Instance),
    memberchk(length-Hs, Instance),
    memberchk(classes-Cs, Instance),
    memberchk(separation-Sep, Instance),
    length(Lefts, N), length(Rights, N), length(Tops, N), length(Bottoms, N),
    length(Rots, N), length(XExt, N), length(YExt, N),

    % Every container lies on the deck.
    Lefts :: 0..DW, Rights :: 0..DW,
    Tops :: 0..DL, Bottoms :: 0..DL,

    % Containers are positioned parallel to the sides of the deck, so a container
    % may be turned by 90 degrees (rotation 1 swaps its width and length).
    Rots :: 0..1,
    ( foreach(W, Ws), foreach(H, Hs), foreach(R, Rots), foreach(XE, XExt), foreach(YE, YExt) do
        XE #= W + R*(H - W),
        YE #= H + R*(W - H)
    ),

    % The containers are cuboid: the far edges follow from the left/top edges and the extents.
    ( foreach(L, Lefts), foreach(Rt, Rights), foreach(XE2, XExt) do
        Rt #= L + XE2
    ),
    ( foreach(T, Tops), foreach(Bt, Bottoms), foreach(YE2, YExt) do
        Bt #= T - YE2
    ),

    make_boxes(Lefts, Rights, Tops, Bottoms, Cs, Boxes),

    % Containers must not overlap, and containers of classes constrained to be separated
    % must keep the minimum distance, either along the deck or across the deck.
    pairwise(Boxes, Sep),

    % Cell view: every deck cell is owned by at most one container, and the owner
    % is the container that covers the cell.
    NC is DW * DL,
    length(Owners, NC),
    Owners :: 0..N,
    cells(Owners, 0, DW, Cells),
    cell_view(Cells, Boxes),

    % The containers fill the deck exactly when their areas add up to the deck area.
    area_sum(Ws, Hs, 0, Area),
    (   Area =:= DW * DL
    ->  NOwn = NC,
        ( foreach(O, Owners) do O #\= 0 )
    ;   NOwn = 0
    ),
    setval(vessel_nown, NOwn),

    (   NOwn =:= 0
    ->  box_vars(Lefts, Tops, Rots, BoxVars),
        append(BoxVars, Owners, Vars)
    ;   append(Owners, Rots, V1), append(V1, Lefts, V2), append(V2, Tops, Vars)
    ),
    Outputs = [left-Lefts, right-Rights, top-Tops, bottom-Bottoms].

% Search: owner cells first (row by row, highest owner first) when the deck is full,
% then the rotations, the lefts and the tops, box by box.
search_goal(Vars) :-
    getval(vessel_nown, NO),
    length(Own, NO),
    append(Own, Rest, Vars),
    search(Own, 0, input_order, indomain_max, complete, []),
    search(Rest, 0, input_order, indomain_min, complete, []).

area_sum([], [], S, S).
area_sum([W|Ws], [H|Hs], S0, S) :-
    S1 is S0 + W * H,
    area_sum(Ws, Hs, S1, S).

make_boxes([], [], [], [], [], []).
make_boxes([L|Ls], [R|Rs], [T|Ts], [B|Bs], [C|Cs], [box(L, R, T, B, C, _Rot)|Bx]) :-
    make_boxes(Ls, Rs, Ts, Bs, Cs, Bx).

box_vars([], [], [], []).
box_vars([L|Ls], [T|Ts], [R|Rs], [R, L, T|Vs]) :-
    box_vars(Ls, Ts, Rs, Vs).

% Owner cells: cell(X, Y, Owner) with index I = Y * DW + X.
cells([], _, _, []).
cells([O|Os], I, DW, [cell(X, Y, O)|Cs]) :-
    X is I mod DW,
    Y is I // DW,
    I1 is I + 1,
    cells(Os, I1, DW, Cs).

% For every cell and every container k: the owner is k exactly when the cell lies
% inside container k. A cell lies inside when left =< x < right and bottom =< y < top.
cell_view([], _).
cell_view([cell(X, Y, O)|Cells], Boxes) :-
    cell_inside_all(Boxes, X, Y, O, 1),
    cell_view(Cells, Boxes).

cell_inside_all([], _, _, _, _).
cell_inside_all([box(L, R, T, B, _C, _)|Boxes], X, Y, O, K) :-
    Cv :: 0..1,
    Cv #= (O #= K),
    A1 :: 0..1, A1 #= (L #=< X),
    A2 :: 0..1, A2 #= (R #> X),
    A3 :: 0..1, A3 #= (B #=< Y),
    A4 :: 0..1, A4 #= (T #> Y),
    Cv #=< A1, Cv #=< A2, Cv #=< A3, Cv #=< A4,
    Cv #>= A1 + A2 + A3 + A4 - 3,
    K1 is K + 1,
    cell_inside_all(Boxes, X, Y, O, K1).

pairwise([], _).
pairwise([Box|Boxes], Sep) :-
    each_pair(Box, Boxes, Sep),
    pairwise(Boxes, Sep).

each_pair(_, [], _).
each_pair(box(L1, R1, T1, B1, C1, _), [box(L2, R2, T2, B2, C2, _)|Boxes], Sep) :-
    nth1(C1, Sep, Row1), nth1(C2, Row1, S12),
    nth1(C2, Sep, Row2), nth1(C1, Row2, S21),
    P1 :: 0..1, P1 #= (R1 + S12 #=< L2),
    P2 :: 0..1, P2 #= (R2 + S21 #=< L1),
    P3 :: 0..1, P3 #= (T1 + S12 #=< B2),
    P4 :: 0..1, P4 #= (T2 + S21 #=< B1),
    P1 + P2 + P3 + P4 #>= 1,
    each_pair(box(L1, R1, T1, B1, C1, _), Boxes, Sep).
