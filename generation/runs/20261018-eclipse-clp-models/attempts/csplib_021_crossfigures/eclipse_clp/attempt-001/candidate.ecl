% Crossfigures (CSPLib 021): a 9x9 grid of digits, black cells and numbered
% answers. Every across or down run of white cells reads as a number (no
% leading zero). The clues relate the answers. M gives the digit in each cell,
% 0 for black cells.

:- lib(ic).

% Layout from the description: x = black cell, w = white cell without a clue
% number, an integer = a white cell with that clue number.
cf_tokens([
    [1,2,w,3,x,4,w,5,6],
    [7,w,x,8,w,w,x,9,w],
    [w,x,10,w,x,11,12,x,w],
    [13,14,w,w,x,15,w,16,w],
    [x,w,x,x,x,x,x,w,x],
    [17,w,18,19,x,20,21,w,22],
    [w,x,23,w,x,24,w,x,w],
    [25,26,x,27,w,w,x,28,w],
    [29,w,w,w,x,30,w,w,w]
]).

model(_Instance, Vars, ['M'-DRows]) :-
    cf_tokens(Toks),
    cf_make_rows(Toks, DRows),
    cf_flat_vars(DRows, Vars),
    cf_across_starts(AS),
    cf_down_starts(DS),
    cf_answers(AS, across, DRows, As),
    cf_answers(DS, down, DRows, Ds),
    cf_clues(As, Ds).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% ---- grid of digits -------------------------------------------------------

cf_make_rows([], []).
cf_make_rows([T|Ts], [D|Ds]) :-
    cf_make_cells(T, D),
    cf_make_rows(Ts, Ds).

cf_make_cells([], []).
cf_make_cells([x|Ts], [0|Ds]) :- !,
    cf_make_cells(Ts, Ds).
cf_make_cells([_|Ts], [V|Ds]) :-
    V :: 0..9,
    cf_make_cells(Ts, Ds).

cf_flat_vars([], []).
cf_flat_vars([Row|Rows], Vs) :-
    cf_row_vars(Row, Vs, Vs1),
    cf_flat_vars(Rows, Vs1).

cf_row_vars([], Vs, Vs).
cf_row_vars([V|Vs0], [V|Vs], Out) :- var(V), !,
    cf_row_vars(Vs0, Vs, Out).
cf_row_vars([_|Vs0], Vs, Out) :-
    cf_row_vars(Vs0, Vs, Out).

% Integers L..H, each once.
cf_range(L, H, X) :-
    L =< H,
    (   X = L
    ;   L < H,
        L1 is L+1,
        cf_range(L1, H, X)
    ).

cf_pick(1, [X|_], X) :- !.
cf_pick(N, [_|T], X) :-
    N1 is N-1,
    cf_pick(N1, T, X).

cf_tok(R, C, T) :-
    cf_tokens(Toks),
    cf_pick(R, Toks, Row),
    cf_pick(C, Row, T).

cf_white(R, C) :-
    R >= 1, R =< 9, C >= 1, C =< 9,
    cf_tok(R, C, T),
    T \== x.

cf_cell(DRows, R, C, V) :-
    cf_pick(R, DRows, Row),
    cf_pick(C, Row, V).

% ---- runs -----------------------------------------------------------------

% Lab-R-C for each across run start (a numbered white cell whose left
% neighbour is not white and whose right neighbour is white).
cf_across_starts(Ss) :-
    findall(Lab-R-C,
            ( cf_range(1, 9, R), cf_range(1, 9, C),
              cf_across_start(R, C, Lab) ),
            Ss).

cf_down_starts(Ss) :-
    findall(Lab-R-C,
            ( cf_range(1, 9, R), cf_range(1, 9, C),
              cf_down_start(R, C, Lab) ),
            Ss).

cf_across_start(R, C, Lab) :-
    cf_tok(R, C, Lab), integer(Lab),
    cf_left_free(R, C),
    C1 is C+1, cf_white(R, C1).

cf_down_start(R, C, Lab) :-
    cf_tok(R, C, Lab), integer(Lab),
    cf_up_free(R, C),
    R1 is R+1, cf_white(R1, C).

cf_left_free(R, C) :-
    ( C =:= 1 -> true ; C0 is C-1, \+ cf_white(R, C0) ).

cf_up_free(R, C) :-
    ( R =:= 1 -> true ; R0 is R-1, \+ cf_white(R0, C) ).

cf_acells(DRows, R, C, [V|Vs]) :-
    cf_cell(DRows, R, C, V),
    C1 is C+1,
    ( cf_white(R, C1) -> cf_acells(DRows, R, C1, Vs) ; Vs = [] ).

cf_dcells(DRows, R, C, [V|Vs]) :-
    cf_cell(DRows, R, C, V),
    R1 is R+1,
    ( cf_white(R1, C) -> cf_dcells(DRows, R1, C, Vs) ; Vs = [] ).

cf_cells(across, DRows, R, C, Vs) :- cf_acells(DRows, R, C, Vs).
cf_cells(down, DRows, R, C, Vs) :- cf_dcells(DRows, R, C, Vs).

% One answer variable per run, equal to the number its digits spell.
cf_answers([], _, _, []).
cf_answers([Lab-R-C|Ss], Dir, DRows, [Lab-Ans|Ps]) :-
    cf_cells(Dir, DRows, R, C, Vs),
    length(Vs, L),
    Lo is 10^(L-1),
    Hi is 10^L - 1,
    Ans :: Lo..Hi,
    cf_post_number(Vs, Ans),
    cf_answers(Ss, Dir, DRows, Ps).

% The answer is the number its digits spell. The expression is written out
% per length, since a sum built at run time is refused by the ic solver.
cf_post_number([D1, D2], A) :-
    A #= 10*D1 + D2.
cf_post_number([D1, D2, D3], A) :-
    A #= 100*D1 + 10*D2 + D3.
cf_post_number([D1, D2, D3, D4], A) :-
    A #= 1000*D1 + 100*D2 + 10*D3 + D4.

ga(N, As, V) :- memberchk(N-V, As).
gd(N, Ds, V) :- memberchk(N-V, Ds).

% Square and prime answers.
cf_square(X) :-
    Y :: 0..99,
    X #= Y*Y.

% The two-digit primes (every answer that is prime here is two digits).
cf_prime(X) :-
    X :: [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97].

% ---- clues ----------------------------------------------------------------

cf_clues(As, Ds) :-
    ga(1, As, A1), ga(4, As, A4), ga(7, As, A7), ga(8, As, A8), ga(9, As, A9),
    ga(10, As, A10), ga(11, As, A11), ga(13, As, A13), ga(15, As, A15),
    ga(17, As, A17), ga(20, As, A20), ga(23, As, A23), ga(24, As, A24),
    ga(25, As, A25), ga(27, As, A27), ga(28, As, A28), ga(29, As, A29),
    ga(30, As, A30),
    gd(1, Ds, D1), gd(2, Ds, D2), gd(3, Ds, D3), gd(4, Ds, D4), gd(5, Ds, D5),
    gd(6, Ds, D6), gd(10, Ds, D10), gd(12, Ds, D12), gd(14, Ds, D14),
    gd(16, Ds, D16), gd(17, Ds, D17), gd(18, Ds, D18), gd(19, Ds, D19),
    gd(20, Ds, D20), gd(21, Ds, D21), gd(22, Ds, D22), gd(26, Ds, D26),
    gd(28, Ds, D28),

    % 1 across: 27 across times two
    A1 #= 2*A27,
    % 4 across: 4 down plus seventy-one
    A4 #= D4 + 71,
    % 7 across: 18 down plus four
    A7 #= D18 + 4,
    % 8 across: 6 down divided by sixteen
    D6 #= 16*A8,
    % 9 across: 2 down minus eighteen
    A9 #= D2 - 18,
    % 10 across: Dozen in six gross (six gross is 864, which is 72 dozen)
    A10 #= 72,
    % 11 across: 5 down minus seventy
    A11 #= D5 - 70,
    % 13 across: 26 down times 23 across
    A13 #= D26*A23,
    % 15 across: 6 down minus 350
    A15 #= D6 - 350,
    % 17 across: 25 across times 23 across
    A17 #= A25*A23,
    % 20 across: A square number
    cf_square(A20),
    % 23 across: A prime number
    cf_prime(A23),
    % 24 across: A square number
    cf_square(A24),
    % 25 across: 20 across divided by seventeen
    A20 #= 17*A25,
    % 27 across: 6 down divided by four
    D6 #= 4*A27,
    % 28 across: Four dozen
    A28 #= 48,
    % 29 across: Seven gross
    A29 #= 1008,
    % 30 across: 22 down plus 450
    A30 #= D22 + 450,

    % 1 down: 1 across plus twenty-seven
    D1 #= A1 + 27,
    % 2 down: Five dozen
    D2 #= 60,
    % 3 down: 30 across plus 888
    D3 #= A30 + 888,
    % 4 down: Two times 17 across
    D4 #= 2*A17,
    % 5 down: 29 across divided by twelve
    A29 #= 12*D5,
    % 6 down: 28 across times 23 across
    D6 #= A28*A23,
    % 10 down: 10 across plus four
    D10 #= A10 + 4,
    % 12 down: Three times 24 across
    D12 #= 3*A24,
    % 14 down: 13 across divided by sixteen
    A13 #= 16*D14,
    % 16 down: 28 down times fifteen
    D16 #= 15*D28,
    % 17 down: 13 across minus 399
    D17 #= A13 - 399,
    % 18 down: 29 across divided by eighteen
    A29 #= 18*D18,
    % 19 down: 22 down minus ninety-four
    D19 #= D22 - 94,
    % 20 down: 20 across minus nine
    D20 #= A20 - 9,
    % 21 down: 25 across minus fifty-two
    D21 #= A25 - 52,
    % 22 down: 20 down times six
    D22 #= 6*D20,
    % 26 down: Five times 24 across
    D26 #= 5*A24,
    % 28 down: 21 down plus twenty-seven
    D28 #= D21 + 27.
