% Diet problem: given the prices and the nutritional requirements (at least)
% for each nutrition type, what is the optimal diet? Minimise the cost of the
% products. Foods: chocolate cake, chocolate ice cream, cola, pineapple
% cheesecake. Nutrition types: calories, chocolate (ounces), sugar (ounces),
% fat (ounces).

:- lib(ic).

% Nutrient content per food (one unit of each food), from the problem table.
calories([400, 200, 150, 500]).
chocolate([3, 2, 0, 0]).
sugar([2, 2, 4, 4]).
fat([2, 4, 1, 5]).

model(Instance, Xs, [cost-Cost], min(Cost)) :-
    memberchk(n-N, Instance),
    memberchk(price-Prices, Instance),
    memberchk(limits-Limits, Instance),
    Limits = [LCal, LChoc, LSugar, LFat],
    length(Xs, N),
    % The number of units of each food is a non-negative integer. The largest
    % requirement is used as the upper bound, derived from the instance.
    ( foreach(L, Limits), fromto(0, A, B, Max) do B is max(A, L) ),
    Xs :: 0..Max,

    % The diet must provide at least the required calories, chocolate, sugar and fat.
    calories(Cal), weighted(Cal, Xs, TCal), TCal #>= LCal,
    chocolate(Choc), weighted(Choc, Xs, TChoc), TChoc #>= LChoc,
    sugar(Sug), weighted(Sug, Xs, TSug), TSug #>= LSugar,
    fat(Fat), weighted(Fat, Xs, TFat), TFat #>= LFat,

    % The cost of the diet is the sum of the prices of the units bought.
    weighted(Prices, Xs, Cost).

% Sum of Coefs[i] * Xs[i].
weighted(Coefs, Xs, Sum) :-
    ( foreach(C, Coefs), foreach(X, Xs), foreach(T, Ts) do T #= C * X ),
    Sum #= sum(Ts).
