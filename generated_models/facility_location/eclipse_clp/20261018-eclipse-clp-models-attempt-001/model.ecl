% Facility location: four candidate warehouses (New York, Los Angeles,
% Chicago, Atlanta) are considered to serve the regions at minimal total cost.
% Each warehouse is open (1) or closed (0). Open warehouses ship at most
% max_shipping units in total. Every region's demand is met exactly.
% Warehouse costs are fixed costs for open warehouses plus unit shipping costs.

:- lib(ic).
:- lib(listut).
:- lib(lists).

model(Instance, Vars, [open_warehouse-Open, ships-Ships, total_cost-Total], min(Total)) :-
    memberchk(fixed_costs-Fixed, Instance),
    memberchk(demands-Demands, Instance),
    memberchk(max_shipping-Max, Instance),
    memberchk(shipping_costs-Costs, Instance),
    length(Fixed, NW),
    length(Demands, NR),
    length(Open, NW),
    Open :: 0..1,
    Open = [NY, LA, _CH, AT],

    % Ships is a warehouse-by-region matrix of shipped units
    length(Ships, NW),
    ( foreach(Row, Ships), param(NR, Max) do
        length(Row, NR),
        Row :: 0..Max
    ),

    % Each region must receive exactly its demand from the warehouses
    % The shipping cost of each region is the sum of its unit costs times the units shipped to it,
    % and it is at least the demand times the cheapest unit cost to that region
    ( for(J, 1, NR), param(Ships, Demands, Costs), foreach(RegionCost, RegionCosts) do
        nth1(J, Demands, D),
        ( foreach(CRow, Costs), foreach(Row, Ships), fromto(0, R0, R1, RegionCost),
          fromto(0, F0, F1, Flow), fromto(1000000, M0, M1, MinC), param(J) do
            nth1(J, CRow, C),
            nth1(J, Row, X),
            R1 #= R0 + C * X,
            F1 #= F0 + X,
            M1 is min(M0, C)
        ),
        Flow #= D,
        RegionCost #>= D * MinC
    ),

    % An open warehouse ships at most max_shipping units; a closed one ships nothing
    ( foreach(Row, Ships), foreach(O, Open), param(Max) do
        sum(Row) #=< Max * O
    ),
    % A cell cannot ship more than the region demands, nor more than the capacity of an open warehouse
    ( foreach(Row, Ships), foreach(O, Open), param(Demands, Max) do
        ( foreach(X, Row), foreach(D, Demands), param(O, Max) do
            X #=< min(Max, D) * O
        )
    ),

    % If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    NY #=< LA,

    % No more than three warehouses can be operational in any given week.
    sum(Open) #=< 3,

    % Either the Atlanta or the Los Angeles warehouse must be opened.
    AT + LA #>= 1,

    % The total cost is the fixed costs of open warehouses plus the shipping costs.
    ( foreach(F, Fixed), foreach(O, Open), foreach(T, FixedTerms) do
        T #= F * O
    ),
    append(FixedTerms, RegionCosts, CostTerms),
    Total #= sum(CostTerms),

    flatten(Ships, FlatShips),
    append(Open, FlatShips, Vars).

search_goal(Vars) :-
    length(Vars, N),
    length(Open, 4),
    append(Open, Ships, Vars),
    length(Ships, NS),
    NS =:= N - 4,
    search(Open, 0, input_order, indomain_min, complete, []),
    search(Ships, 0, smallest, indomain_min, complete, []).
