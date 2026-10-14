:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Facility location: decide which of four candidate warehouses to open and how
% many units each ships to each region, meeting every region's demand at the
% least total cost (fixed cost of the open warehouses plus shipping cost),
% subject to three rules about which warehouses may be open together.

% Search: the open/closed decisions first, closing warehouses first (fewest
% fixed costs first), then the shipments from the cheapest warehouse-region
% pairs to the dearest, splitting each domain in half and trying the upper half
% first, so a plan ships greedily along cheap pairs and the optimality proof
% reasons over intervals instead of single shipment values.
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

    % Implied, for the capacity limit (a Lagrangian bound): for prices
    % p[i] >= 0 charged per unit a warehouse sends,
    %   shipping cost + sum over i of p[i] * (units warehouse i sends)
    %     = sum over pairs of (unit cost + p[i]) * units
    %     >= sum over regions of demand * the cheapest priced rate of an open
    %        warehouse to that region,
    % because a closed warehouse sends nothing and every region receives at
    % least its demand. With each warehouse sending at most max_shipping, this
    % bounds the shipping cost where capacity, rather than the cheapest rate,
    % decides who serves a region; the per-region bounds above assume the
    % cheapest open warehouse can serve every region it is cheapest for.
    % The candidate price vectors charge at most two warehouses, each at 0 or
    % at a gap between its unit cost to some region and a dearer warehouse's
    % cost to that region (the prices at which the bound changes slope). Each
    % candidate is a valid bound, but posting them all (hundreds) slows every
    % search step, so only the strongest candidate for each open/closed
    % pattern is posted: the one with the largest right-hand side when every
    % open warehouse sends max_shipping. The right-hand side depends only on
    % which warehouses are open, so it is read from a table over the
    % open/closed patterns, computed from the instance costs and demands.
    maplist(load, Ships, Loads),
    findall(Lambda, price_vector(NW, ShippingCosts, Lambda), Lambdas0),
    sort(Lambdas0, Candidates),
    findall(Best, ( open_pattern(NW, Pattern),
                    strongest_price(Candidates, Pattern, RegionCosts, Demands,
                                    MaxShipping, Best) ), Chosen0),
    sort(Chosen0, Lambdas),
    maplist(price_bound(NW, Open, Loads, RegionCosts, Demands, ShippedTotal), Lambdas),

    % shipments labelled cheapest pair first (instance data decides the order)
    ship_order(ShippingCosts, Ships, OrderedShips),
    append(Levels, LevelVars),
    % Closed[i] = 1 - Open[i], labelled in place of Open so that, with the
    % upper half tried first, a warehouse is tried closed before open
    maplist(closed, Open, Closed),
    append([Closed, OrderedShips, LevelVars, RegionCostVars, [Total]], Vars).

closed(IsOpen, IsClosed) :-
    IsClosed in 0..1,
    IsClosed #= 1 - IsOpen.

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

breakpoints(W, ShippingCosts, Prices) :-
    findall(P, price(W, ShippingCosts, P), Ps),
    sort([0|Ps], Prices).

% Lambda charges warehouse W the price P and warehouse V the price Q, W < V,
% and nothing to the others; the all-zero vector is left out (the per-region
% bounds already cover it)
price_vector(NW, ShippingCosts, Lambda) :-
    between(1, NW, W),
    between(1, NW, V),
    W < V,
    breakpoints(W, ShippingCosts, PricesW),
    breakpoints(V, ShippingCosts, PricesV),
    member(P, PricesW),
    member(Q, PricesV),
    P + Q > 0,
    numlist(1, NW, Is),
    maplist(price_at(W, P, V, Q), Is, Lambda).

price_at(W, P, V, Q, I, L) :-
    (   I =:= W -> L = P
    ;   I =:= V -> L = Q
    ;   L = 0
    ).

% shipping cost + sum of Lambda[i] * load[i] >= Bound, with Bound the table
% value for the open/closed pattern of the warehouses
price_bound(NW, Open, Loads, RegionCosts, Demands, ShippedTotal, Lambda) :-
    findall(Row,
            ( open_pattern(NW, Pattern),
              priced_demand(RegionCosts, Demands, Lambda, Pattern, Bound0),
              append(Pattern, [Bound0], Row) ),
            Rows),
    append(Open, [Bound], Tuple),
    tuples_in([Tuple], Rows),
    scalar_product(Lambda, Loads, #=, Priced),
    ShippedTotal + Priced #>= Bound.

% Best = the candidate price vector with the largest bound for Pattern when
% each open warehouse sends max_shipping units (the first such in the
% candidate order on ties)
strongest_price(Candidates, Pattern, RegionCosts, Demands, MaxShipping, Best) :-
    findall(NegValue-Lambda,
            ( member(Lambda, Candidates),
              priced_demand(RegionCosts, Demands, Lambda, Pattern, Bound),
              scalar_product_ground(Lambda, Pattern, Charged),
              NegValue is -(Bound - MaxShipping * Charged) ),
            Valued),
    keysort(Valued, [_-Best|_]).

scalar_product_ground(Xs, Ys, P) :-
    foldl([X, Y, P0, P1]>>(P1 is P0 + X * Y), Xs, Ys, 0, P).

% a 0/1 pattern with at least one open warehouse (rule 3 needs one)
open_pattern(NW, Pattern) :-
    length(Pattern, NW),
    maplist(between(0, 1), Pattern),
    sum_list(Pattern, NOpen),
    NOpen > 0.

% sum over regions of demand * the cheapest priced rate among the warehouses
% open in Pattern
priced_demand(RegionCosts, Demands, Lambda, Pattern, Bound) :-
    foldl(region_priced(Lambda, Pattern), RegionCosts, Demands, 0, Bound).

region_priced(Lambda, Pattern, Costs, Demand, Bound0, Bound) :-
    findall(Rate, ( nth1(I, Pattern, 1), nth1(I, Costs, C), nth1(I, Lambda, L),
                    Rate is C + L ), Rates),
    min_list(Rates, Cheapest),
    Bound is Bound0 + Demand * Cheapest.

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
