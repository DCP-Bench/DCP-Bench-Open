:- lib(ic).
:- lib(ic_edge_finder).
:- lib(ic_cumulative).
:- lib(branch_and_bound).
:- lib(timeout).

jobs([[[2, 1], [0, 3], [1, 6], [3, 7], [5, 3], [4, 6]],
      [[1, 8], [2, 5], [4, 10], [5, 10], [0, 10], [3, 4]],
      [[2, 5], [3, 4], [5, 8], [0, 9], [1, 1], [4, 7]],
      [[1, 5], [0, 5], [2, 5], [3, 3], [4, 8], [5, 9]],
      [[2, 9], [1, 3], [4, 5], [5, 4], [0, 3], [3, 1]],
      [[1, 3], [3, 3], [5, 9], [0, 10], [4, 4], [2, 1]]]).

:- dynamic inst/1.
:- dynamic rseed/1.
rseed(1).
rnd(R, Max) :- retract(rseed(X)), X1 is (X*1103515245 + 12345) mod 2147483648, assert(rseed(X1)), R is (X1 // 65536) mod Max.

gen_jobs(N, S, Jobs) :-
    retract(rseed(_)), assert(rseed(S)),
    ( for(_, 1, N), foreach(J, Jobs), param(N) do
        ( for(M, 0, N-1), foreach(K-M, Keyed), param(N) do rnd(K, 1000000) ),
        sort(1, =<, Keyed, Sorted),
        ( foreach(_-M2, Sorted), foreach([M2,D], J) do rnd(D0, 9), D is D0 + 1 )
    ).

mk_recs([], _, []).
mk_recs([[M,D]|Rest], H, [t(M,S,D)|Ts]) :- S :: 0..H, mk_recs(Rest, H, Ts).

chain([_]).
chain([t(_,S1,D1), t(M2,S2,D2)|Rest]) :- S1 + D1 #=< S2, chain([t(M2,S2,D2)|Rest]).

on_machine(_, [], [], []).
on_machine(M, [t(M1,S,D)|Ts], Ss, Ds) :-
    ( M1 == M -> Ss = [S|Ss1], Ds = [D|Ds1] ; Ss = Ss1, Ds = Ds1 ),
    on_machine(M, Ts, Ss1, Ds1).

last_end([t(_,S,D)], S + D) :- !.
last_end([_|R], E) :- last_end(R, E).

% pairwise no-overlap with reified disjunction
pairwise([], []).
pairwise([S|Ss], [D|Ds]) :- ( foreach(S2, Ss), foreach(D2, Ds), param(S, D) do ( S + D #=< S2 or S2 + D2 #=< S ) ), pairwise(Ss, Ds).

post_machine(ef, Ss, Ds) :- ic_edge_finder:disjunctive(Ss, Ds).
post_machine(ef3, Ss, Ds) :- ic_edge_finder3:disjunctive(Ss, Ds).
post_machine(cum, Ss, Ds) :- ( foreach(_, Ss), foreach(1, Rs) do true ), ic_cumulative:cumulative(Ss, Ds, Rs, 1).
post_machine(efcum, Ss, Ds) :- ( foreach(_, Ss), foreach(1, Rs) do true ), ic_edge_finder:cumulative(Ss, Ds, Rs, 1).
post_machine(pair, Ss, Ds) :- pairwise(Ss, Ds).

jobs_of(ft06, J) :- jobs(J).
jobs_of(gen(N,S), J) :- gen_jobs(N, S, J).

build(Inst, Var, Starts, Mk) :-
    jobs_of(Inst, Jobs), length(Jobs, NM), NM1 is NM - 1,
    ( foreach(J, Jobs), fromto(0, H0, H1, H) do ( foreach([_,D], J), fromto(H0, A, B, H1) do B is A + D ) ),
    ( foreach(J, Jobs), foreach(Recs, JR), foreach(E, Ends), param(H) do mk_recs(J, H, Recs), chain(Recs), last_end(Recs, E) ),
    flatten(JR, All),
    ( for(M, 0, NM1), param(All, Var) do on_machine(M, All, Ss, Ds), post_machine(Var, Ss, Ds) ),
    Mk #= max(Ends),
    ( foreach(t(_,S,_), All), foreach(S, Starts) do true ).

run(Var, Sel, Val, Strat) :- run(ft06, Var, Sel, Val, Strat).
run(Inst, Var, Sel, Val, Strat) :-
    cputime(T0),
    ( timeout(( build(Inst, Var, Starts, Mk),
        bb_min(search(Starts, 0, Sel, Val, complete, []), Mk, bb_options{strategy:Strat, report_success:true/0, report_failure:true/0}),
        MkV = Mk ), 60, (MkV = timeout)) -> true ; MkV = failed ),
    cputime(T1), T is T1 - T0,
    printf("%w %w %w %w %w: makespan %w in %.2f s cpu%n", [Inst, Var, Sel, Val, Strat, MkV, T]).
run_bbt(Inst, Var, Sel, Val, Secs) :-
    cputime(T0),
    build(Inst, Var, Starts, Mk),
    bb_min(search(Starts, 0, Sel, Val, complete, []), Mk, bb_options{timeout:Secs, report_success:true/0, report_failure:true/0}),
    cputime(T1), T is T1 - T0,
    printf("bb timeout %w s: makespan %w after %.2f s cpu%n", [Secs, Mk, T]).
mark_timeout :- setval(timed_out, true).
run_bbt2(Inst, Var, Sel, Val, Secs) :-
    setval(timed_out, false),
    build(Inst, Var, Starts, Mk),
    bb_min(search(Starts, 0, Sel, Val, complete, []), Mk, bb_options{timeout:Secs, report_success:true/0, report_failure:true/0, report_timeout:mark_timeout/0}),
    getval(timed_out, TO),
    printf("makespan %w, timed out: %w%n", [Mk, TO]).
