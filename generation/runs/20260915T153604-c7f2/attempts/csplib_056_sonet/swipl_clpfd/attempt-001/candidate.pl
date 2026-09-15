:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% SONET ring assignment: put every communicating pair of nodes on a shared
% ring, within each ring's node capacity, using as few add-drop multiplexers
% as possible.
model(Instance, Vars, [ring_config-Rings, total_adms-TotalAdms],
      min(TotalAdms)) :-
    R = Instance.r,
    N = Instance.n,
    Demand = Instance.demand,
    Capacity = Instance.capacity_nodes,
    length(Rings, R),
    maplist({N}/[Ring]>>(length(Ring, N), Ring ins 0..1), Rings),
    append(Rings, Vars),
    % Nodes with traffic between them must meet on some ring.
    numlist(1, N, Nodes),
    maplist({Rings, Demand, N}/[I]>>together(Rings, Demand, N, I), Nodes),
    maplist([Ring, Cap]>>sum(Ring, #=<, Cap), Rings, Capacity),
    % One multiplexer per node-to-ring assignment.
    sum(Vars, #=, TotalAdms).

together(Rings, Demand, N, I) :-
    Next is I + 1,
    (   Next > N
    ->  true
    ;   numlist(Next, N, Others),
        nth1(I, Demand, Row),
        maplist({Rings, Row, I}/[J]>>share_ring(Rings, Row, I, J), Others)
    ).

share_ring(Rings, Row, I, J) :-
    nth1(J, Row, Traffic),
    (   Traffic > 0
    ->  maplist({I, J}/[Ring, Both]>>
                    (nth1(I, Ring, Here), nth1(J, Ring, There),
                     Here + There #= 2 #<==> Both),
                Rings, Shared),
        sum(Shared, #>=, 1)
    ;   true
    ).
