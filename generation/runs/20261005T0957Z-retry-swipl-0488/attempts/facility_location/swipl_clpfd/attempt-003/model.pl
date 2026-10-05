:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).

% Facility location: decide which of four candidate warehouses to open and how
% many units each ships to each region, meeting every region's demand at the
% least total cost (fixed cost of the open warehouses plus shipping cost),
% subject to three rules about which warehouses may be open together.

% Search: the open/closed decisions first, then the shipments from the
% cheapest warehouse-region pairs to the dearest, splitting each domain in
% half and trying the upper half first, so the first plan found ships greedily
% along cheap pairs and the optimality proof reasons over intervals instead of
% single shipment values.
labeling_options([leftmost, down, bisect]).

model(Instance, Vars,
      [total_cost-Total, open_warehouse-Open, ships-Ships], min(Total)) :-
    Names = Instance.warehouse_s,            % warehouse cities
    FixedCosts = Instance.fixed_costs,       % weekly fixed cost of each warehouse
    MaxShipping = Instance.max_shipping,     % most units one warehouse can send per week
    Demands = Instance.demands,              % weekly demand of each region
    ShippingCosts = Instance.shipping_costs, % cost per unit from warehouse i to region j
    length(Names, NW),
    length(Demands, NR),
    nth1(NewYork, Names, 'New York'),
    nth1(LosAngeles, Names, 'Los Angeles'),
    nth1(Atlanta, Names, 'Atlanta'),

    % Open[i] is 1 when warehouse i is open
    length(Open, NW),
    Open ins 0..1,
    % Ships[i][j] = units sent from warehouse i to region j, 0..max_shipping
    length(Ships, NW),
    maplist(ship_row(NR, MaxShipping), Ships),

    % a warehouse sends at most max_shipping units, and nothing when it is closed
    maplist(capacity(MaxShipping), Ships, Open),

    % every region receives at least its demand
    transpose(Ships, Regions),
    maplist(meets_demand, Regions, Demands),

    % 1. if the New York warehouse is open, the Los Angeles one must be open too
    nth1(NewYork, Open, OpenNewYork),
    nth1(LosAngeles, Open, OpenLosAngeles),
    OpenNewYork #=< OpenLosAngeles,
    % 2. at most three warehouses are open
    sum(Open, #=<, 3),
    % 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    nth1(Atlanta, Open, OpenAtlanta),
    OpenAtlanta + OpenLosAngeles #>= 1,

    % Implied: the open warehouses together can cover the total demand, since
    % everything shipped is at most max_shipping per open warehouse and at
    % least the sum of the demands.
    sum_list(Demands, TotalDemand),
    sum(Open, #=, NOpen),
    MaxShipping * NOpen #>= TotalDemand,

    % shipping cost of each region = sum over warehouses of unit cost * units
    transpose(ShippingCosts, RegionCosts),
    maplist(region_cost(NW, MaxShipping), RegionCosts, Regions, RegionCostVars, Levels),
    % Level[1] of a region is everything it receives, so it is at least the
    % demand; stated on the level as well, since clpfd does not carry the
    % demand from the column sum over to the chain of levels
    maplist(receives_demand, Levels, Demands),

    % total cost = fixed costs of the open warehouses + shipping cost of every
    % region; 0..10000 is the reference's domain for total_cost
    Total in 0..10000,
    scalar_product(FixedCosts, Open, #=, FixedTotal),
    sum(RegionCostVars, #=, ShippedTotal),
    Total #= FixedTotal + ShippedTotal,

    % Implied, for the capacity limit: for a warehouse w and any price p >= 0,
    %   shipping cost + p * (units w sends)
    %     = sum over pairs of (unit cost, raised by p when sent from w) * units
    %     >= sum over regions of demand * the cheapest raised rate of an open
    %        warehouse to that region,
    % because a closed warehouse sends nothing. With the units w sends at most
    % max_shipping, this bounds the shipping cost where capacity, rather than
    % the cheapest rate, decides who serves a region: the per-region bounds
    % above assume the cheapest open warehouse serves every region it is
    % cheapest for, however many units that adds up to. The bound is posted for
    % every warehouse w and every price p at which w's raised rate to some
    % region reaches another warehouse's rate (the prices at which the bound
    % can change slope).
    maplist(load, Ships, Loads),
    numlist(1, NW, Warehouses),
    findall(W-P, ( member(W, Warehouses), price(W, ShippingCosts, P) ), Prices0),
    sort(Prices0, Prices),
    maplist(capacity_price_bound(Open, Loads, RegionCosts, Demands, ShippedTotal), Prices),

    % shipments labelled cheapest pair first (instance data decides the order)
    ship_order(ShippingCosts, Ships, OrderedShips),
    append(Levels, LevelVars),
    append([Open, OrderedShips, LevelVars, RegionCostVars, [Total]], Vars).

ship_row(NR, MaxShipping, Row) :-
    length(Row, NR),
    Row ins 0..MaxShipping.

capacity(MaxShipping, Row, IsOpen) :-
    sum(Row, #=<, MaxShipping * IsOpen).

meets_demand(Column, Demand) :-
    sum(Column, #>=, Demand).

% The cost of region j is the scalar product of its unit costs and its
% shipments. It is restated, as an implied constraint, by ranking the
% warehouses by unit cost to j: with Level[k] the units received from the
% warehouses ranked k or worse, the cost equals
%   c(1) * Level[1] + sum over k >= 2 of (c(k) - c(k-1)) * Level[k],
% an exact identity (summation by parts). Every coefficient is nonnegative and
% Level[1] >= demand, so a bound on the total cost caps how many units can come
% from the dearer warehouses, which the scalar product alone does not propagate.
region_cost(NW, MaxShipping, Costs, Column, RegionCost, Levels) :-
    max_list([0|Costs], MaxCost),
    Top is NW * MaxShipping * MaxCost,
    RegionCost in 0..Top,
    scalar_product(Costs, Column, #=, RegionCost),
    length(Costs, NCosts),
    numlist(1, NCosts, Positions),
    maplist(cost_key, Costs, Positions, Column, Keyed),
    msort(Keyed, Ranked),
    pairs_keys_values(Ranked, RankedKeys, RankedShips),
    pairs_keys(RankedKeys, RankedCosts),
    LevelTop is NW * MaxShipping,
    suffix_levels(RankedShips, LevelTop, Levels),
    steps(RankedCosts, 0, Steps),
    scalar_product(Steps, Levels, #=, RegionCost).

load(Row, Load) :- sum(Row, #=, Load).

% P is the gap between warehouse W's unit cost to some region and the higher
% unit cost of another warehouse to the same region
price(W, ShippingCosts, P) :-
    nth1(W, ShippingCosts, RowW),
    nth1(K, ShippingCosts, RowK),
    K =\= W,
    nth1(J, RowW, CW),
    nth1(J, RowK, CK),
    P is CK - CW,
    P > 0.

capacity_price_bound(Open, Loads, RegionCosts, Demands, ShippedTotal, W-P) :-
    nth1(W, Loads, LoadW),
    maplist(cheapest_raised_rate(Open, W, P), RegionCosts, Rates),
    scalar_product(Demands, Rates, #=, Bound),
    ShippedTotal + P * LoadW #>= Bound.

% Rate = the lowest unit cost to one region over the open warehouses, with
% warehouse W's cost raised by P. A closed warehouse's term is raised above
% every cost, so it is never the minimum while some warehouse is open.
cheapest_raised_rate(Open, W, P, Costs, Rate) :-
    max_list(Costs, MaxCost),
    Big is MaxCost + P + 1,
    length(Costs, N),
    numlist(1, N, Is),
    maplist(raised_term(W, P, Big), Is, Costs, Open, Terms),
    min_expression(Terms, Expression),
    Rate #= Expression.

raised_term(W, P, Big, I, Cost, IsOpen, Raised + Big * (1 - IsOpen)) :-
    (   I =:= W -> Raised is Cost + P ; Raised = Cost ).

min_expression([T], T) :- !.
min_expression([T|Ts], min(T, E)) :- min_expression(Ts, E).

receives_demand([Received|_], Demand) :- Received #>= Demand.

% Levels[k] = sum of the ranked shipments from position k to the end
suffix_levels([], _, []).
suffix_levels([S|Ss], Top, [L|Ls]) :-
    L in 0..Top,
    suffix_levels(Ss, Top, Ls),
    (   Ls = [Next|_] -> L #= S + Next ; L #= S ).

% Steps[k] = c(k) - c(k-1), with c(0) = 0
steps([], _, []).
steps([C|Cs], Previous, [Step|Steps]) :-
    Step is C - Previous,
    steps(Cs, C, Steps).

% Shipment variables ordered by unit cost, cheapest pair first; ties keep the
% warehouse-major order of the instance.
ship_order(ShippingCosts, Ships, Ordered) :-
    append(ShippingCosts, CellCosts),
    append(Ships, Cells),
    length(Cells, N),
    numlist(1, N, Positions),
    maplist(cost_key, CellCosts, Positions, Cells, Keyed),
    msort(Keyed, Sorted),
    pairs_values(Sorted, Ordered).

cost_key(Cost, Position, Cell, (Cost-Position)-Cell).
