:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Facility location: decide which of four candidate warehouses to open and how
% many units each ships to each region, meeting every region's demand at the
% least total cost (fixed cost of the open warehouses plus shipping cost),
% subject to three rules about which warehouses may be open together.
model(Instance, Vars,
      [total_cost-Total, open_warehouse-Open, ships-Ships], min(Total)) :-
    Names = Instance.warehouse_s,           % warehouse cities
    FixedCosts = Instance.fixed_costs,      % weekly fixed cost of each warehouse
    MaxShipping = Instance.max_shipping,    % most units one warehouse can send per week
    Demands = Instance.demands,             % weekly demand of each region
    ShippingCosts = Instance.shipping_costs, % cost per unit from warehouse i to region j
    length(Names, NWarehouses),
    length(Demands, NRegions),
    nth1(NewYork, Names, 'New York'),
    nth1(LosAngeles, Names, 'Los Angeles'),
    nth1(Atlanta, Names, 'Atlanta'),

    % Open[i] is 1 when warehouse i is open
    length(Open, NWarehouses),
    Open ins 0..1,
    % Ships[i][j] = units sent from warehouse i to region j (0 for a closed warehouse)
    length(Ships, NWarehouses),
    maplist({NRegions, MaxShipping}/[Row]>>(length(Row, NRegions), Row ins 0..MaxShipping), Ships),

    % a warehouse sends at most max_shipping units, and nothing when it is closed
    maplist({MaxShipping}/[Row, IsOpen]>>(sum(Row, #=<, MaxShipping * IsOpen)), Ships, Open),

    % every region receives at least its demand
    transpose(Ships, Regions),
    maplist([Column, Demand]>>sum(Column, #>=, Demand), Regions, Demands),

    % 1. if the New York warehouse is open, the Los Angeles one must be open too
    nth1(NewYork, Open, OpenNewYork),
    nth1(LosAngeles, Open, OpenLosAngeles),
    OpenNewYork #=< OpenLosAngeles,
    % 2. at most three warehouses are open
    sum(Open, #=<, 3),
    % 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    nth1(Atlanta, Open, OpenAtlanta),
    OpenAtlanta + OpenLosAngeles #>= 1,

    % total cost = fixed costs of the open warehouses + cost of everything shipped
    append(Ships, Cells),
    append(ShippingCosts, CellCosts),
    Total in 0..10000,
    scalar_product(FixedCosts, Open, #=, FixedTotal),
    scalar_product(CellCosts, Cells, #=, ShippedTotal),
    Total #= FixedTotal + ShippedTotal,
    append([Open, Cells, [Total]], Vars).
