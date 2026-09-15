:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Revenue maximization: sell fare packages within each package's demand and
% each flight leg's seat count, for the most revenue.
model(Instance, Sell, [packages_to_sell-Sell, max_revenue-Revenue],
      max(Revenue)) :-
    Seats = Instance.available_seats,
    Demand = Instance.demand,
    Prices = Instance.revenue,
    Delta = Instance.delta,
    length(Demand, NumPackages),
    length(Sell, NumPackages),
    max_list(Demand, MaxDemand),
    Sell ins 0..MaxDemand,
    maplist([S, Cap]>>(S #=< Cap), Sell, Demand),
    % delta is indexed package-then-leg, so seats per leg need the transpose.
    transpose(Delta, ByLeg),
    maplist({Sell}/[Uses, Available]>>
                scalar_product(Uses, Sell, #=<, Available),
            ByLeg, Seats),
    scalar_product(Prices, Sell, #=, Revenue).
