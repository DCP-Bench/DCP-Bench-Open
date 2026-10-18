% ACC basketball schedule, 1997/98 (CSPLib 011).
% Double round robin of NT teams over ND dates with the mirroring scheme, the home/away/bye
% patterns, the weekend pattern, rival matches, opponent sequences and the other constraints
% of the description.
% Indices are 0-based. Teams: 0 Clem, 1 Duke, 2 FSU, 3 GT, 4 UMD, 5 UNC, 6 NCSt, 7 UVA, 8 Wake.
% config[d][i] is the opponent of team i on date d; a bye is config[d][i] = i.
% where[d][i] is 0 for home, 1 for bye, 2 for away.

:- lib(ic).
:- lib(ic_global).
:- lib(listut).

model(Instance, Vars, [config-Config, where-Where]) :-
    memberchk(n_teams-NT, Instance),
    memberchk(n_days-ND, Instance),
    NT1 is NT - 1,
    ND1 is ND - 1,
    matrix(ND, NT, 0, NT1, Config),
    matrix(ND, NT, 0, 2, Where),
    % code of a cell is 9 * where + config: a team's column then counts its home games
    % against each opponent (codes 0..8), its byes (codes 9..17) and its away games (18..26)
    matrix(ND, NT, 0, 26, Code),
    V = m(NT, ND, Config, Where, Code),

    % the three matrices agree on every date
    acc_each(0, ND1, cell_rules(V)),

    % every team: each opponent once at home and once away, two byes, the patterns
    acc_each(0, NT1, team_rules(V)),

    % mirroring scheme of the description: the same opponent on each paired dates
    mirror_pairs(V, [0-7, 1-8, 2-11, 3-12, 4-13, 5-14, 6-15, 9-16, 10-17]),

    % rival matches: on the last date each team except FSU meets its rival, plays FSU or has a bye
    rival_last(Config, ND1, [0-3, 3-0, 1-5, 5-1, 4-7, 7-4, 6-8, 8-6]),

    % constrained matches: in dates 11 to 18 (0-based 10 to ND1)
    meet_later(Config, ND1, 8, 5),
    meet_later(Config, ND1, 8, 1),
    meet_later(Config, ND1, 3, 5),
    meet_later(Config, ND1, 3, 1),

    % other constraints of item 9 (dates 0-based)
    at(Config, 1, 5, X1), X1 #= 0,          % UNC plays Clem in the second date
    at(Config, ND1, 5, X2), X2 #= 1,        % UNC plays Duke in the last date
    at(Config, 10, 5, X3), X3 #= 1,         % UNC plays Duke in date 11
    at(Config, 15, 1, X4), X4 #= 1,         % Duke has a bye in date 16
    at(Config, 0, 8, X5), X5 #= 8,          % Wake has a bye in the first date
    at(Where, 16, 8, X6), X6 #\= 0,         % Wake does not play home in date 17
    not_at(Where, ND1, 0, 2),               % Clem, Duke, UMD, Wake not away in the last date
    not_at(Where, ND1, 1, 2),
    not_at(Where, ND1, 4, 2),
    not_at(Where, ND1, 8, 2),
    not_at(Where, 0, 0, 2),                 % Clem, FSU, GT, Wake not away in the first date
    not_at(Where, 0, 2, 2),
    not_at(Where, 0, 3, 2),
    not_at(Where, 0, 8, 2),
    not_at(Where, ND1, 2, 1),               % neither FSU nor NCSt has a bye in the last date
    not_at(Where, ND1, 6, 1),
    not_at(Where, 0, 5, 1),                 % UNC has no bye in the first date

    flatten(Config, Vars).

% ---- helpers -------------------------------------------------------------

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

acc_each(Lo, Hi, G) :-
    (   Lo > Hi
    ->  true
    ;   call(G, Lo),
        Lo1 is Lo + 1,
        acc_each(Lo1, Hi, G)
    ).

matrix(0, _, _, _, []) :- !.
matrix(N, NT, Lo, Hi, [Row|Rows]) :-
    N > 0,
    length(Row, NT),
    dom_list(Row, Lo, Hi),
    N1 is N - 1,
    matrix(N1, NT, Lo, Hi, Rows).

dom_list([], _, _).
dom_list([X|Xs], Lo, Hi) :-
    X :: Lo..Hi,
    dom_list(Xs, Lo, Hi).

at(M, D, I, X) :-
    nth0(D, M, Row),
    nth0(I, Row, X).

not_at(M, D, I, Val) :-
    at(M, D, I, X),
    X #\= Val.

% cells of column I on the dates Ds
pick(_, _, [], []).
pick(M, I, [D|Ds], [X|Xs]) :-
    at(M, D, I, X),
    pick(M, I, Ds, Xs).

range(L, H, [L|T]) :-
    L =< H,
    !,
    L1 is L + 1,
    range(L1, H, T).
range(_, _, []).

% dates whose 0-based index has parity P (P=1: weekend dates 2, 4, ..., 18)
dates_mod(D, DE, _, []) :-
    D > DE,
    !.
dates_mod(D, DE, P, Ds) :-
    (   D mod 2 =:= P
    ->  Ds = [D|Rest]
    ;   Ds = Rest
    ),
    D1 is D + 1,
    dates_mod(D1, DE, P, Rest).

% not all of the pairs X-V hold at once
forbid_conj(Pairs) :-
    neq_disj(Pairs, G),
    call(G).

neq_disj([X-V], (X #\= V)).
neq_disj([X-V|T], ((X #\= V) or G)) :-
    T = [_|_],
    neq_disj(T, G).

% ---- dates -------------------------------------------------------------------

% one date: codes, venues and the involution config[d][config[d][i]] = i
cell_rules(V, D) :-
    V = m(NT, _, C, W, K),
    NT1 is NT - 1,
    nth0(D, C, RowC),
    nth0(D, W, RowW),
    nth0(D, K, RowK),
    acc_each(0, NT1, cell_team(RowC, RowW, RowK)).

cell_team(RowC, RowW, RowK, I) :-
    nth0(I, RowW, Wi),
    nth0(I, RowC, Ci),
    nth0(I, RowK, Ki),
    Ki #= 9 * Wi + Ci,
    ( (Wi #= 1) <=> (Ci #= I) ),
    X1 #= Ci + 1,
    element(X1, RowC, I),
    element(X1, RowW, Wo),
    Wi + Wo #= 2.

% ---- teams -------------------------------------------------------------------

team_rules(V, I) :-
    V = m(_, ND, _, W, K),
    ND1 is ND - 1,
    ND2 is ND - 2,
    % codes of the column: each opponent once at home, once away, two byes
    range(0, ND1, AllDates),
    pick(K, I, AllDates, KCol),
    range(0, 26, Vals),
    code_counts(Vals, I, KCol),
    % weekends (0-based odd dates): four home, four away, one bye
    dates_mod(0, ND1, 1, Weekends),
    pick(W, I, Weekends, WW),
    occurrences(0, WW, 4),
    occurrences(2, WW, 4),
    occurrences(1, WW, 1),
    % home or bye on at least two of the first five weekends
    length(First5, 5),
    append(First5, _, Weekends),
    pick(W, I, First5, W5),
    occurrences(2, W5, N5),
    N5 #=< 3,
    % no team plays away on both last dates
    pick(W, I, [ND2, ND1], AL),
    occurrences(2, AL, NL),
    NL #=< 1,
    % windows of consecutive dates
    S3 is ND - 3,
    acc_each(0, S3, win3(V, I)),
    S4 is ND - 4,
    acc_each(0, S4, win4(V, I)),
    S5 is ND - 5,
    acc_each(0, S5, win5(V, I)),
    % opponent sequences: no consecutive away games against UNC (5) and Duke (1)
    acc_each(0, ND2, opp_pair(V, I)),
    % no three consecutive dates against UNC, Duke and Wake, in any order
    (   member(I, [1, 5, 8])
    ->  true
    ;   acc_each(0, S3, triple_rules(V, I))
    ).

% count of code Val in the column of team I
code_counts([], _, _).
code_counts([Val|Vs], I, Col) :-
    code_count(Val, I, N),
    occurrences(Val, Col, N),
    code_counts(Vs, I, Col).

code_count(Val, I, N) :-
    (   Val =< 8
    ->  ( Val =:= I -> N = 0 ; N = 1 )
    ;   Val =< 17
    ->  ( Val - 9 =:= I -> N = 2 ; N = 0 )
    ;   ( Val - 18 =:= I -> N = 0 ; N = 1 )
    ).

% windows of consecutive dates starting at S
win3(V, I, S) :-
    V = m(_, _, _, W, _),
    E is S + 2,
    range(S, E, Ds),
    pick(W, I, Ds, Ws),
    occurrences(2, Ws, N2),
    N2 #=< 2,
    occurrences(0, Ws, N0),
    N0 #=< 2.

win4(V, I, S) :-
    V = m(_, _, _, W, _),
    E is S + 3,
    range(S, E, Ds),
    pick(W, I, Ds, Ws),
    occurrences(0, Ws, N0),
    N0 #>= 1.

win5(V, I, S) :-
    V = m(_, _, _, W, _),
    E is S + 4,
    range(S, E, Ds),
    pick(W, I, Ds, Ws),
    occurrences(2, Ws, N2),
    N2 #>= 1.

% UNC = 5, Duke = 1: no away game at one of them on date d and at the other on date d+1
opp_pair(V, I, D) :-
    V = m(_, _, C, W, _),
    D1 is D + 1,
    at(C, D, I, C0), at(W, D, I, W0),
    at(C, D1, I, C1), at(W, D1, I, W1),
    forbid_conj([C0-5, W0-2, C1-1, W1-2]),
    forbid_conj([C0-1, W0-2, C1-5, W1-2]).

% the three opponents on dates D, D+1, D+2 are not UNC (5), Duke (1), Wake (8) in any order
triple_rules(V, I, D) :-
    V = m(_, _, C, _, _),
    D1 is D + 1,
    D2 is D + 2,
    at(C, D, I, X0), at(C, D1, I, X1), at(C, D2, I, X2),
    forbid_conj([X0-1, X1-5, X2-8]),
    forbid_conj([X0-1, X1-8, X2-5]),
    forbid_conj([X0-5, X1-1, X2-8]),
    forbid_conj([X0-5, X1-8, X2-1]),
    forbid_conj([X0-8, X1-1, X2-5]),
    forbid_conj([X0-8, X1-5, X2-1]).

% ---- constraints across teams ----------------------------------------------

mirror_pairs(_, []).
mirror_pairs(V, [R1-R2|Ps]) :-
    V = m(NT, _, C, _, _),
    NT1 is NT - 1,
    acc_each(0, NT1, mirror_team(C, R1, R2)),
    mirror_pairs(V, Ps).

mirror_team(C, R1, R2, I) :-
    at(C, R1, I, X),
    at(C, R2, I, Y),
    X #= Y.

rival_last(_, _, []).
rival_last(C, D, [I-R|Ps]) :-
    at(C, D, I, X),
    X :: [R, 2, I],
    rival_last(C, D, Ps).

% team A meets team B (both 0-based) on at least one date from 10 to the last date
meet_later(C, ND1, A, B) :-
    range(10, ND1, Ds),
    pick(C, A, Ds, Cs),
    or_eq(Cs, B, G),
    call(G).

or_eq([X], V, (X #= V)).
or_eq([X|Xs], V, ((X #= V) or G)) :-
    Xs = [_|_],
    or_eq(Xs, V, G).
