% csplib_056_sonet: SONET network design. Nodes are placed on rings through
% add-drop multiplexers (ADMs). Ring k hosts at most capacity_nodes[k] nodes.
% Every pair of nodes with traffic demand must share at least one ring.
% Minimise the total number of ADMs used.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [ring_config-Rows, total_adms-Total], min(Total)) :-
    memberchk(n-N, Instance),
    memberchk(r-R, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(capacity_nodes-Caps, Instance),
    % ring_config[k][i] is 1 if node i is on ring k
    length(Rows, R),
    ( foreach(Row, Rows), param(N) do
        length(Row, N),
        Row :: 0..1
    ),
    % ring k hosts at most capacity_nodes[k] nodes
    ( foreach(Row, Rows), foreach(C, Caps) do
        sum(Row) #=< C
    ),
    % two nodes with traffic demand between them share at least one ring
    ( for(I, 0, N-1), param(Rows, Demand, N) do
        ( for(J, I+1, N-1), param(Rows, Demand, I) do
            ( traffic(Demand, I, J) ->
                share_ring(Rows, I, J)
            ;   true
            )
        )
    ),
    % total number of ADMs is the number of node placements
    flatten(Rows, Vars),
    sum(Vars) #= Total,
    Total #>= 0.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% the column of node I across all rings
column(Rows, I, Col) :-
    ( foreach(Row, Rows), foreach(X, Col), param(I) do
        nth0(I, Row, X)
    ).

% demand in either direction between nodes I and J
traffic(Demand, I, J) :-
    nth0(I, Demand, RowI),
    nth0(J, RowI, D1),
    nth0(J, Demand, RowJ),
    nth0(I, RowJ, D2),
    ( D1 > 0 ; D2 > 0 ).

% nodes I and J are both on some common ring
share_ring(Rows, I, J) :-
    column(Rows, I, ColI),
    column(Rows, J, ColJ),
    ( foreach(X, ColI), foreach(Y, ColJ), foreach(Z, Both) do
        Z #= X * Y
    ),
    sum(Both) #>= 1.
