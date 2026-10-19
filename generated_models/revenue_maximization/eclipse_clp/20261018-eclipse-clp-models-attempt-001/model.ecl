% Revenue maximization: flight legs with a limited passenger capacity, and
% itinerary packages sold as one unit with a price and an estimated demand.
% Decide how many units of each package to sell to maximize the total revenue.
% Seats are reserved according to the number of packages sold.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [max_revenue-Rev, packages_to_sell-Vars], max(Rev)) :-
    memberchk(demand-Demand, Instance),
    memberchk(revenue-Price, Instance),
    memberchk(available_seats-Seats, Instance),
    memberchk(delta-Delta, Instance),
    length(Demand, NP),
    length(Seats, NL),
    length(Vars, NP),

    % The number of units of each package sold is between 0 and its estimated demand.
    ( foreach(X, Vars), foreach(D, Demand) do
        X #:: 0..D
    ),

    % The passenger seats on each flight leg are reserved by the packages using it:
    % the units sold of every package, times its use of the leg, must fit the leg's seats.
    ( for(L, 1, NL), param(Vars, Delta, Seats) do
        nth1(L, Seats, Cap),
        ( foreach(X, Vars), foreach(Row, Delta), foreach(T, Terms), param(L) do
            nth1(L, Row, Use),
            T #= Use * X
        ),
        sum(Terms) #=< Cap
    ),

    % The total revenue is the sum of the price of each package times the units sold.
    ( foreach(X, Vars), foreach(P, Price), foreach(R, Revs) do
        R #= P * X
    ),
    Rev #= sum(Revs).
