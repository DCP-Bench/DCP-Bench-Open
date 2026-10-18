% Solitaire battleships (CSPLib 014).
% The grid has one variable per square. Each square takes one of the codes read
% from the instance: water, submarine (CIRCLE), or a ship part (LEFT, RIGHT, TOP,
% BOTTOM, MIDDLE). The fleet, the row and column counts and the hints come from the
% instance. The grid is padded with water so every square has four neighbours.

:- lib(ic).
:- lib(lists).

model(Instance, Vars, [grid-Rows]) :-
    memberchk(rows-R, Instance),
    memberchk(cols-C, Instance),
    memberchk('WATER'-W, Instance),
    memberchk('CIRCLE'-CI, Instance),
    memberchk('LEFT'-LF, Instance),
    memberchk('RIGHT'-RT, Instance),
    memberchk('TOP'-TP, Instance),
    memberchk('BOTTOM'-BT, Instance),
    memberchk('MIDDLE'-MD, Instance),
    memberchk(fleet_counts-Fleet, Instance),
    memberchk(rowsum-RowSum, Instance),
    memberchk(colsum-ColSum, Instance),
    memberchk(hints-Hints, Instance),
    K = k(W, CI, LF, RT, TP, BT, MD),
    Codes = [W, CI, LF, RT, TP, BT, MD],
    make_rows(R, C, Codes, Rows),
    C2 is C + 2,
    border(C2, W, Brow),
    pad_rows(Rows, W, PRows),
    append([Brow|PRows], [Brow], P),
    Last is R + 1,
    Cend is C + 1,
    rules_rows(2, Last, Cend, P, K),
    post_hints(Hints, P),
    ship_rows(Rows, W, SRows),
    sum_rows(SRows, RowSum),
    transpose_list(SRows, SCols),
    sum_rows(SCols, ColSum),
    post_fleet(Fleet, P, R, C, K),
    flatten(Rows, Vars).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Grid construction

make_rows(0, _, _, []) :- !.
make_rows(N, C, Codes, [Row|Rows]) :-
    N > 0,
    make_cells(C, Codes, Row),
    N1 is N - 1,
    make_rows(N1, C, Codes, Rows).

make_cells(0, _, []) :- !.
make_cells(N, Codes, [X|Xs]) :-
    N > 0,
    X :: Codes,
    N1 is N - 1,
    make_cells(N1, Codes, Xs).

border(0, _, []) :- !.
border(N, W, [W|Xs]) :-
    N > 0,
    N1 is N - 1,
    border(N1, W, Xs).

pad_rows([], _, []).
pad_rows([Row|Rows], W, [PR|PRs]) :-
    append([W|Row], [W], PR),
    pad_rows(Rows, W, PRs).

% cell(+P, +I, +J, -V): padded 1-based access
cell(P, I, J, V) :-
    pick(I, P, Row),
    pick(J, Row, V).

pick(1, [X|_], X) :- !.
pick(N, [_|T], X) :-
    N > 1,
    N1 is N - 1,
    pick(N1, T, X).

% Shape rules: a ship part's neighbours are water, except along its own ship,
% and no two ships touch, not even diagonally.

rules_rows(I, Last, _, _, _) :- I > Last, !.
rules_rows(I, Last, Cend, P, K) :-
    rules_cols(2, I, Cend, P, K),
    I1 is I + 1,
    rules_rows(I1, Last, Cend, P, K).

rules_cols(J, _, Cend, _, _) :- J > Cend, !.
rules_cols(J, I, Cend, P, K) :-
    cell_rules(I, J, P, K),
    J1 is J + 1,
    rules_cols(J1, I, Cend, P, K).

cell_rules(I, J, P, k(W, CI, LF, RT, TP, BT, MD)) :-
    cell(P, I, J, V),
    I1 is I - 1, I2 is I + 1, J1 is J - 1, J2 is J + 1,
    cell(P, I1, J, U), cell(P, I2, J, D),
    cell(P, I, J1, Lf), cell(P, I, J2, Rt),
    cell(P, I1, J1, Ul), cell(P, I1, J2, Ur),
    cell(P, I2, J1, Dl), cell(P, I2, J2, Dr),
    % a left part continues to the right and is alone above and below
    (V #= LF) => (Rt #= RT or Rt #= MD),
    (V #= LF) => (Lf #= W),
    (V #= LF) => (U #= W),
    (V #= LF) => (D #= W),
    % a right part is continued from the left and is alone above and below
    (V #= RT) => (Lf #= LF or Lf #= MD),
    (V #= RT) => (Rt #= W),
    (V #= RT) => (U #= W),
    (V #= RT) => (D #= W),
    % a top part continues downwards and is alone left and right
    (V #= TP) => (D #= BT or D #= MD),
    (V #= TP) => (U #= W),
    (V #= TP) => (Lf #= W),
    (V #= TP) => (Rt #= W),
    % a bottom part is continued from above and is alone left and right
    (V #= BT) => (U #= TP or U #= MD),
    (V #= BT) => (D #= W),
    (V #= BT) => (Lf #= W),
    (V #= BT) => (Rt #= W),
    % a submarine has water on all four sides
    (V #= CI) => (U #= W),
    (V #= CI) => (D #= W),
    (V #= CI) => (Lf #= W),
    (V #= CI) => (Rt #= W),
    % a middle part is either horizontal or vertical
    (V #= MD) => (((Lf #= LF or Lf #= MD) and (Rt #= RT or Rt #= MD) and (U #= W) and (D #= W))
                  or ((U #= TP or U #= MD) and (D #= BT or D #= MD) and (Lf #= W) and (Rt #= W))),
    % ships do not touch diagonally
    (V #\= W) => (Ul #= W),
    (V #\= W) => (Ur #= W),
    (V #\= W) => (Dl #= W),
    (V #\= W) => (Dr #= W).

% Hints: [Row, Col, Code], 0-based

post_hints([], _).
post_hints([[R, Cc, Code]|Hs], P) :-
    I is R + 2,
    J is Cc + 2,
    cell(P, I, J, V),
    V #= Code,
    post_hints(Hs, P).

% Row and column counts of ship squares

ship_rows([], _, []).
ship_rows([Row|Rows], W, [Ss|Sss]) :-
    ship_row(Row, W, Ss),
    ship_rows(Rows, W, Sss).

ship_row([], _, []).
ship_row([V|Vs], W, [S|Ss]) :-
    S #= (V #\= W),
    ship_row(Vs, W, Ss).

sum_rows([], []).
sum_rows([Ss|Sss], [N|Ns]) :-
    sum(Ss) #= N,
    sum_rows(Sss, Ns).

transpose_list([[]|_], []) :- !.
transpose_list(M, [Col|Cols]) :-
    firsts_rests(M, Col, Rest),
    transpose_list(Rest, Cols).

firsts_rests([], [], []).
firsts_rests([[H|T]|Rs], [H|Hs], [T|Ts]) :-
    firsts_rests(Rs, Hs, Ts).

% Fleet: [Length, Count] pairs. A ship of length L starts at one square (a
% submarine for L = 1, a left part for a horizontal ship, a top part for a
% vertical one) and is counted once, through the product of its square codes.

post_fleet([], _, _, _, _).
post_fleet([[Len, Cnt]|Fs], P, R, C, K) :-
    Last is R + 1,
    Cend is C + 1,
    fleet_rows(2, Last, Len, P, Cend, K, Bs, []),
    sum(Bs) #= Cnt,
    post_fleet(Fs, P, R, C, K).

fleet_rows(I, Last, _, _, _, _, Bs, Bs) :- I > Last, !.
fleet_rows(I, Last, Len, P, Cend, K, Bs0, Bs) :-
    fleet_cols(2, I, Last, Cend, Len, P, K, Bs0, Bs1),
    I1 is I + 1,
    fleet_rows(I1, Last, Len, P, Cend, K, Bs1, Bs).

fleet_cols(J, _, _, Cend, _, _, _, Bs, Bs) :- J > Cend, !.
fleet_cols(J, I, Last, Cend, Len, P, K, Bs0, Bs) :-
    start_ind(Len, I, J, P, K, lim(Last, Cend), Bs0, Bs1),
    J1 is J + 1,
    fleet_cols(J1, I, Last, Cend, Len, P, K, Bs1, Bs).

start_ind(1, I, J, P, k(_, CI, _, _, _, _, _), _, [B|Bs], Bs) :-
    cell(P, I, J, V),
    B #= (V #= CI).
start_ind(Len, I, J, P, k(_, _, LF, RT, TP, BT, MD), lim(Rend, Cend), Bs0, Bs) :-
    Len > 1,
    (   J + Len - 1 =< Cend
    ->  path_codes(Len, LF, MD, RT, HC),
        ind_list(I, J, 0, 1, 0, HC, P, HB),
        prod_list(HB, HP),
        Bs0 = [HP|Bs1]
    ;   Bs0 = Bs1
    ),
    (   I + Len - 1 =< Rend
    ->  path_codes(Len, TP, MD, BT, VC),
        ind_list(I, J, 1, 0, 0, VC, P, VB),
        prod_list(VB, VP),
        Bs1 = [VP|Bs]
    ;   Bs1 = Bs
    ).

% codes along a ship of length Len: first, middles, last
path_codes(Len, F, M, L, [F|Cs]) :-
    Mids is Len - 2,
    mid_codes(Mids, M, Ms),
    append(Ms, [L], Cs).

mid_codes(0, _, []) :- !.
mid_codes(N, M, [M|Ms]) :-
    N > 0,
    N1 is N - 1,
    mid_codes(N1, M, Ms).

% one indicator per square of the line, starting at (I,J) and stepping (Di,Dj)
ind_list(_, _, _, _, _, [], _, []).
ind_list(I, J, Di, Dj, Off, [Code|Codes], P, [B|Bs]) :-
    I2 is I + Off * Di,
    J2 is J + Off * Dj,
    cell(P, I2, J2, V),
    B #= (V #= Code),
    Off1 is Off + 1,
    ind_list(I, J, Di, Dj, Off1, Codes, P, Bs).

% product of 0/1 indicators
prod_list([B], B) :- !.
prod_list([B|Bs], Prod) :-
    prod_list(Bs, Q),
    Prod #= B * Q.
