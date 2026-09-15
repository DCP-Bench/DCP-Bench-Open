:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Fixed charge: a product can only be made on a rented machine.  Maximize
% sales profit minus the rent paid, within the labor and cloth capacities.
model(Instance, Vars, [z-Z], max(Z)) :-
    NumMachines = Instance.num_machines,
    NumProducts = Instance.num_products,
    MaxProduction = Instance.max_production,
    RentingCost = Instance.renting_cost,
    Capacity = Instance.capacity,
    Resources = Instance.resources,
    Product = Instance.product,
    Use = Instance.use,
    length(Rent, NumMachines),
    Rent ins 0..1,
    length(Produce, NumProducts),
    Produce ins 0..MaxProduction,
    % Profit bound 0..10000 is the reference's declared domain for z.
    Z in 0..10000,
    append([[Z], Rent, Produce], Vars),
    maplist([Row, Profit]>>nth0(0, Row, Profit), Product, Profits),
    scalar_product(Profits, Produce, #=, Income),
    scalar_product(RentingCost, Rent, #=, Rents),
    Z #= Income - Rents,
    % Each resource column of `use` is consumed within its capacity.
    transpose(Use, ByResource),
    maplist({ByResource, Capacity, Produce}/[R]>>
                resource_limit(ByResource, Capacity, Produce, R),
            Resources),
    % Nothing is produced on a machine that was not rented.  The reference
    % indexes `rent` by product index, so index rather than walk the two lists
    % in step: there is no guarantee they are the same length.
    LastProduct is NumProducts - 1,
    numlist(0, LastProduct, ProductIndices),
    maplist({Produce, Rent, MaxProduction}/[P]>>
                rent_needed(Produce, Rent, MaxProduction, P),
            ProductIndices).

rent_needed(Produce, Rent, MaxProduction, P) :-
    nth0(P, Produce, Quantity),
    nth0(P, Rent, Machine),
    Quantity #=< MaxProduction * Machine.

resource_limit(ByResource, Capacity, Produce, R) :-
    nth0(R, ByResource, Usage),
    nth0(R, Capacity, Limit),
    scalar_product(Usage, Produce, #=<, Limit).
