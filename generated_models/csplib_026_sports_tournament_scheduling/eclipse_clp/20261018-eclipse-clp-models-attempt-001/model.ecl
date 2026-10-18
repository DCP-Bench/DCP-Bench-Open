% Sports tournament scheduling (CSPLib 026).
% N teams play over N-1 weeks. Each week has N/2 periods of two slots: the first
% team in a slot plays at home, the second plays away.
% Every team plays once a week; every team plays at most twice in the same period
% over the tournament; every team plays every other team.

:- lib(ic).
:- lib(ic_global).
:- lib(ic_mdd).
:- lib(listut).
:- import alldifferent/1 from ic_global.

model(Instance, Vars, [home-HomeRows, away-AwayRows]) :-
    memberchk(n_teams-N, Instance),
    W is N - 1,
    P is N // 2,
    M is N * (N - 1) // 2,
    make_matrix(W, P, HomeRows),
    make_matrix(W, P, AwayRows),
    make_matrix(W, P, PairRows),
    flatten(HomeRows, HomeFlat),
    flatten(AwayRows, AwayFlat),
    flatten(PairRows, PairFlat),
    HomeFlat :: 1..N,
    AwayFlat :: 1..N,
    PairFlat :: 1..M,

    % every team plays once a week
    week_alldiff(HomeRows, AwayRows),

    % every team plays every other team
    % (each unordered pair of teams gets its own index, and each index is used once)
    pair_tuples(N, PairTuples),
    post_cells(HomeFlat, AwayFlat, PairFlat, PairTuples),
    alldifferent(PairFlat),

    % every team plays at most twice in the same period over the tournament
    period_limits(P, N, HomeRows, AwayRows),

    append(HomeFlat, AwayFlat, HA),
    append(HA, PairFlat, Vars).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

make_matrix(W, P, Rows) :-
    length(Rows, W),
    ( foreach(R, Rows), param(P) do length(R, P) ).

week_alldiff([], []).
week_alldiff([Hr|Hs], [Ar|As]) :-
    append(Hr, Ar, Week),
    alldifferent(Week),
    week_alldiff(Hs, As).

% all unordered pairs I < J, each with an index K, as tuples [home, away, K] in both orders
pair_tuples(N, Rows) :-
    interval(1, N, Teams),
    findall(I-J, (member(I, Teams), I1 is I + 1, interval(I1, N, Js), member(J, Js)), Pairs),
    number_pairs(Pairs, 1, Rows).

interval(L, H, []) :- L > H, !.
interval(L, H, [L|Xs]) :- L1 is L + 1, interval(L1, H, Xs).

number_pairs([], _, []).
number_pairs([I-J|Ps], K, [[I, J, K], [J, I, K]|Rs]) :-
    K1 is K + 1,
    number_pairs(Ps, K1, Rs).

% each cell (home, away, pair index) must be one of the allowed tuples
post_cells([], [], [], _).
post_cells([H|Hs], [A|As], [Q|Qs], Rows) :-
    table([[H, A, Q]], Rows),
    post_cells(Hs, As, Qs, Rows).

column([], _, []).
column([R|Rs], P, [X|Xs]) :-
    nth1(P, R, X),
    column(Rs, P, Xs).

period_limits(P, N, HomeRows, AwayRows) :-
    ( for(Pc, 1, P), param(N, HomeRows, AwayRows) do
        column(HomeRows, Pc, HC),
        column(AwayRows, Pc, AC),
        append(HC, AC, Col),
        ( for(T, 1, N), param(Col) do
            atmost(2, Col, T)
        )
    ).
