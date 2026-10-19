% Fixed charge production planning: a company manufactures shirts, shorts and
% pants. Each product requires a number of hours of labor and a certain amount
% of cloth (use, one row per product, one column per resource), and the company
% has a limited capacity of both.
% All of these products can be manufactured only by renting an appropriate
% machine (shirtM, shortM, pantM), and each machine has a renting cost.
% The profit of each product (product[p][0]) excludes the cost of renting.
% The company would like to maximize its profit; z is the maximum profit.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [z-Z], max(Z)) :-
    memberchk(product-ProductRows, Instance),
    memberchk(use-UseRows, Instance),
    memberchk(capacity-Capacity, Instance),
    memberchk(renting_cost-RentCost, Instance),
    memberchk(max_production-MaxP, Instance),
    memberchk(shirtM-ShirtM, Instance),
    memberchk(shortM-ShortM, Instance),
    memberchk(pantM-PantM, Instance),
    length(ProductRows, NP),
    length(Prod, NP),
    Prod :: 0..MaxP,
    length(RentCost, NM),
    length(Rent, NM),
    Rent :: 0..1,

    % Each product requires a number of hours of labor and an amount of cloth,
    % and the company has a limited capacity of both.
    length(Capacity, NR),
    ( for(R, 1, NR), param(UseRows, Prod, Capacity) do
        nth1(R, Capacity, Cap),
        column_terms(R, UseRows, Prod, Terms),
        sum(Terms) #=< Cap
    ),

    % All of these products can be manufactured only by renting an appropriate
    % machine: a product can be made only if its machine is rented.
    machine_links(Prod, [ShirtM, ShortM, PantM], Rent, MaxP),

    % The company would like to maximize its profit (excluding the cost of
    % renting the equipment), with the profit of each product from the data.
    column_terms(1, ProductRows, Prod, ProfitTerms),
    weighted(RentCost, Rent, CostTerms),
    Z #= sum(ProfitTerms) - sum(CostTerms),

    append(Prod, Rent, Vars).

% column_terms(+C, +Rows, +Xs, -Terms): Terms = [A*X ...] with A the C-th entry of each row
column_terms(_, [], [], []).
column_terms(C, [Row|Rows], [X|Xs], [A*X|Ts]) :-
    nth1(C, Row, A),
    column_terms(C, Rows, Xs, Ts).

% weighted(+Coeffs, +Xs, -Terms): Terms = [C*X ...]
weighted([], [], []).
weighted([C|Cs], [X|Xs], [C*X|Ts]) :-
    weighted(Cs, Xs, Ts).

% machine_links(+Prod, +Machines, +Rent, +MaxP): a product's output is at most
% MaxP when its machine is rented, and 0 otherwise
machine_links([], [], _, _).
machine_links([X|Xs], [M|Ms], Rent, MaxP) :-
    Idx is M + 1,
    nth1(Idx, Rent, Y),
    X #=< MaxP * Y,
    machine_links(Xs, Ms, Rent, MaxP).
