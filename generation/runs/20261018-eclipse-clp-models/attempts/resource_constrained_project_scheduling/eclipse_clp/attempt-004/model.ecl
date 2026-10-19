% Resource-constrained project scheduling (RCPSP).
% The jobs have durations and a need for each renewable resource. Each resource
% has a capacity that the jobs running at the same time must not exceed.
% Precedence arcs [Pred, Succ] say that Succ starts only after Pred has finished.
% Jobs are 0-based; the first and last jobs are dummy jobs of duration 0.
% Find the start time of every job that minimises the makespan.

:- lib(ic).
:- lib(ic_edge_finder3).
:- lib(branch_and_bound).
:- lib(listut).
:- lib(lists).

model(Instance, Vars, [start_time-Starts], min(Makespan)) :-
    memberchk(durations_data-Ds, Instance),
    memberchk(resource_needs_data-Needs, Instance),
    memberchk(resource_capacities_data-Caps, Instance),
    memberchk(successors_link_data-Arcs, Instance),
    length(Ds, N),
    length(Caps, R),
    ( foreach(D, Ds), fromto(0, A, B, Horizon) do B is A + D ),
    length(Starts, N),
    Starts :: 0..Horizon,
    Makespan :: 0..Horizon,

    % every job finishes at its start time plus its duration
    ( foreach(S, Starts), foreach(D, Ds), foreach(E, Ends) do E #= S + D ),

    % precedence: the successor starts after the predecessor has finished
    ( foreach([P, Q], Arcs), param(Starts, Ds) do
        nth0(P, Starts, SP),
        nth0(P, Ds, DP),
        nth0(Q, Starts, SQ),
        SP + DP #=< SQ
    ),

    % resource capacity: at every time, the demand of the running jobs stays within capacity
    % (jobs with zero duration or zero demand cannot take capacity and are left out)
    ( for(K, 1, R), param(Starts, Ds, Needs, Caps) do
        ( foreach(S, Starts), foreach(D, Ds), foreach(Row, Needs), param(K),
          fromto([], S0, S1, Ss), fromto([], D0, D1, Dd), fromto([], V0, V1, Vv) do
            nth1(K, Row, V),
            ( D > 0, V > 0 -> S1 = [S|S0], D1 = [D|D0], V1 = [V|V0]
            ; S1 = S0, D1 = D0, V1 = V0 )
        ),
        nth1(K, Caps, Cap),
        cumulative(Ss, Dd, Vv, Cap)
    ),

    % redundant: jobs that cannot run together form cliques; the jobs of a clique run one after the other
    ( for(I, 0, N - 1), foreach(Row, Adj), param(N, Ds, Needs, Caps) do
        nth0(I, Ds, DI), nth0(I, Needs, RI),
        ( for(J, 0, N - 1), foreach(F, Row), param(I, DI, RI, Ds, Needs, Caps) do
            nth0(J, Ds, DJ), nth0(J, Needs, RJ),
            ( I \== J, DI > 0, DJ > 0, conflict(RI, RJ, Caps) -> F = 1 ; F = 0 )
        )
    ),
    % the pairs that conflict are ordered one way or the other
    ( for(K, 0, N - 1), foreach(K, Idx) do true ),
    findall(I-J, ( member(I, Idx), member(J, Idx), I < J, nth0(I, Adj, RowI), nth0(J, RowI, 1) ), Edges),
    ( foreach(I-J, Edges), foreach(Bo, Bs), param(Starts, Ds, Horizon) do
        nth0(I, Starts, SI), nth0(I, Ds, DI), nth0(J, Starts, SJ), nth0(J, Ds, DJ),
        Bo :: 0..1,
        SI + DI #=< SJ + Horizon * (1 - Bo),
        SJ + DJ #=< SI + Horizon * Bo
    ),
    append(Bs, Starts, Vs0),
    append(Vs0, [Makespan], Vars),
    clique_cover(Adj, N, Cliques),
    ( foreach(Cl, Cliques), param(Starts, Ds) do
        ( foreach(K, Cl), foreach(SK, Sc), foreach(DK, Dc), param(Starts, Ds) do
            nth0(K, Starts, SK), nth0(K, Ds, DK)
        ),
        disjunctive(Sc, Dc)
    ),

    % makespan: no job ends after it
    ( foreach(E, Ends), param(Makespan) do
        Makespan #>= E
    ),

    % makespan: the resource requirements of all jobs, divided by the resource capacity, bound the makespan from below
    ( for(K, 1, R), param(Ds, Needs, Caps, Makespan) do
        ( foreach(D, Ds), foreach(Row, Needs), param(K), fromto(0, A, B, Energy) do
            nth1(K, Row, V),
            B is A + D * V
        ),
        nth1(K, Caps, Cap),
        LB is (Energy + Cap - 1) // Cap,
        Makespan #>= LB
    ).

conflict(RI, RJ, Caps) :-
    ( foreach(A, RI), foreach(B, RJ), foreach(C, Caps), foreach(F, Flags) do
        ( A + B > C -> F = 1 ; F = 0 )
    ),
    memberchk(1, Flags).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% greedy cover of all incompatible pairs by cliques (data-derived)
clique_cover(Adj, N, Cliques) :-
    N1 is N - 1,
    ( for(I, 0, N1), fromto([], C0, C1, Cliques), fromto([], V0, V1, _), param(Adj, N1) do
        nth0(I, Adj, Row),
        ( for(J, I + 1, N1), fromto(C0-V0, CV0, CV1, C1-V1), param(I, Row, Adj, N1) do
            nth0(J, Row, F),
            CV0 = Cs0-Cov0,
            ( F =:= 1, \+ memberchk(I-J, Cov0) ->
                grow([I, J], Adj, N1, Mem0),
                msort(Mem0, Mem),
                pairs_of(Mem, Ps),
                append(Ps, Cov0, Cov1),
                CV1 = [Mem|Cs0]-Cov1
            ; CV1 = CV0 )
        )
    ).

grow(Mem0, Adj, N1, Mem) :-
    ( for(K, 0, N1), fromto(Mem0, M0, M1, Mem), param(Adj) do
        ( \+ memberchk(K, M0), all_adjacent(K, M0, Adj) -> M1 = [K|M0] ; M1 = M0 )
    ).

all_adjacent(K, Mem, Adj) :-
    nth0(K, Adj, Row),
    ( foreach(M, Mem), param(Row) do nth0(M, Row, 1) ).

pairs_of([], []).
pairs_of([X|Xs], Ps) :-
    ( foreach(Y, Xs), foreach(X-Y, Ps0), param(X) do true ),
    pairs_of(Xs, Ps1),
    append(Ps0, Ps1, Ps).
