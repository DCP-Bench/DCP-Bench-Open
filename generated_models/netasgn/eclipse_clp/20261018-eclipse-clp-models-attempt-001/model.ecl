% Project assignment problem: assign hours from people to projects at minimum cost.
% Person i has Supply_i hours, project j needs Demand_j hours, the cost per hour is
% Cost_{i,j}, and person i can contribute at most Limit_{i,j} hours to project j.
% Output assign[i][j] (hours from person i to project j) and total_cost.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [assign-Assign, total_cost-Total], min(Total)) :-
    memberchk(supply-Supply, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(cost-Cost, Instance),
    memberchk(limit-Limit, Instance),
    length(Supply, N),
    length(Demand, M),
    length(Assign, N),
    ( foreach(Row, Assign), param(M) do length(Row, M) ),

    % the hours assigned from each person i to project j are at most Limit_{i,j}
    ( foreach(Row, Assign), foreach(LimRow, Limit) do
        ( foreach(X, Row), foreach(L, LimRow) do X :: 0..L )
    ),

    % the total number of hours assigned from each person i equals its supply
    ( foreach(Row, Assign), foreach(Si, Supply) do
        sum(Row) #= Si
    ),

    % the total number of hours assigned to each project j equals its demand
    project_demand(Assign, Demand, 1),

    % total_cost is the sum of cost per hour times the hours assigned
    ( foreach(Row, Assign), foreach(CostRow, Cost), foreach(Terms, TermsList) do
        ( foreach(X, Row), foreach(C, CostRow), foreach(T, Terms) do T #= C * X )
    ),
    flatten(TermsList, AllTerms),
    sum(AllTerms) #= Total,

    flatten(Assign, Vars).

% the column of project J (1-based) across all people sums to Demand
project_demand(_, [], _).
project_demand(Assign, [Dj | Ds], J) :-
    ( foreach(Row, Assign), foreach(X, Col), param(J) do nth1(J, Row, X) ),
    sum(Col) #= Dj,
    J1 is J + 1,
    project_demand(Assign, Ds, J1).
