:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Aircraft assignment: choose how many aircraft of each type fly each route so
% every route's passenger demand is met, no type is used beyond its fleet, and
% the total operating cost is minimal.
model(Instance, Vars, [allocation-Rows], min(Cost)) :-
    Availability = Instance.availability,   % aircraft available per type
    Demand = Instance.demand,               % passengers to carry per route
    Capabilities = Instance.capabilities,   % passengers a type carries on a route
    Costs = Instance.costs,                 % cost of one aircraft of a type on a route
    length(Availability, NTypes),
    length(Demand, NRoutes),
    max_list(Availability, MostAircraft),

    % Rows[i][j] = number of aircraft of type i assigned to route j; a type
    % never needs more aircraft on one route than its whole fleet
    length(Rows, NTypes),
    maplist({NRoutes, MostAircraft}/[Row]>>(length(Row, NRoutes), Row ins 0..MostAircraft), Rows),

    % a type cannot be assigned more aircraft than are available
    maplist([Row, Available]>>sum(Row, #=<, Available), Rows, Availability),

    % the aircraft on each route together carry at least the route's demand
    transpose(Rows, RouteColumns),
    transpose(Capabilities, CapabilityColumns),
    maplist([Column, Carried, Wanted]>>scalar_product(Carried, Column, #>=, Wanted),
            RouteColumns, CapabilityColumns, Demand),

    % total operating cost of the assignment
    append(Rows, Cells),
    append(Costs, CellCosts),
    sum_list(CellCosts, CostSum),
    Bound is MostAircraft * CostSum,
    Cost in 0..Bound,
    scalar_product(CellCosts, Cells, #=, Cost),
    append(Cells, [Cost], Vars).
