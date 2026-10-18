% Resource-constrained project scheduling (RCPSP).
% The jobs have durations and a need for each renewable resource. Each resource
% has a capacity that the jobs running at the same time must not exceed.
% Precedence arcs [Pred, Succ] say that Succ starts only after Pred has finished.
% Jobs are 0-based; the first and last jobs are dummy jobs of duration 0.
% Find the start time of every job that minimises the makespan.

:- lib(ic).
:- lib(ic_edge_finder).
:- lib(branch_and_bound).
:- lib(listut).

model(Instance, Starts, [start_time-Starts], min(Makespan)) :-
    memberchk(durations_data-Ds, Instance),
    memberchk(resource_needs_data-Needs, Instance),
    memberchk(resource_capacities_data-Caps, Instance),
    memberchk(successors_link_data-Arcs, Instance),
    length(Ds, N),
    length(Caps, R),
    ( foreach(D, Ds), fromto(0, A, B, Horizon) do B is A + D ),
    length(Starts, N),
    Starts :: 0..Horizon,

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
    ( for(K, 1, R), param(Starts, Ds, Needs, Caps) do
        ( foreach(Row, Needs), foreach(V, Col), param(K) do
            nth1(K, Row, V)
        ),
        nth1(K, Caps, Cap),
        cumulative(Starts, Ds, Col, Cap)
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

search_goal(Starts) :-
    search(Starts, 0, input_order, indomain_min, complete, []).
