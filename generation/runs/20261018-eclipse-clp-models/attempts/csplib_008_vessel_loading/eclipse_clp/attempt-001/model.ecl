% Vessel loading (CSPLib prob008): place the containers on a rectangular deck,
% without overlapping, and respecting the minimum separations between classes.
% Containers are cuboid, laid out in a single layer, and may be rotated by 90 degrees
% so that they stay parallel to the sides of the deck.
% Outputs: left, right, top, bottom as 0-based positions; right = left + extent along the
% deck width, bottom = top + extent along the deck length.

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

    % The deck area is rectangular: every container lies on the deck.
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
        Bt #= T + YE2
    ),

    % Containers must not overlap, and containers of classes constrained to be separated
    % must keep the minimum distance, either along the deck or across the deck.
    make_boxes(Lefts, Rights, Tops, Bottoms, Cs, Boxes),
    pairwise(Boxes, Sep),

    append(Lefts, Tops, LT),
    append(LT, Rots, Vars),
    Outputs = [left-Lefts, right-Rights, top-Tops, bottom-Bottoms].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

make_boxes([], [], [], [], [], []).
make_boxes([L|Ls], [R|Rs], [T|Ts], [B|Bs], [C|Cs], [box(L, R, T, B, C)|Bx]) :-
    make_boxes(Ls, Rs, Ts, Bs, Cs, Bx).

pairwise([], _).
pairwise([Box|Boxes], Sep) :-
    each_pair(Box, Boxes, Sep),
    pairwise(Boxes, Sep).

each_pair(_, [], _).
each_pair(box(L1, R1, T1, B1, C1), [box(L2, R2, T2, B2, C2)|Boxes], Sep) :-
    nth1(C1, Sep, Row1), nth1(C2, Row1, S12),
    nth1(C2, Sep, Row2), nth1(C1, Row2, S21),
    (   R1 + S12 #=< L2
    or  R2 + S21 #=< L1
    or  B1 + S12 #=< T2
    or  B2 + S21 #=< T1
    ),
    each_pair(box(L1, R1, T1, B1, C1), Boxes, Sep).
