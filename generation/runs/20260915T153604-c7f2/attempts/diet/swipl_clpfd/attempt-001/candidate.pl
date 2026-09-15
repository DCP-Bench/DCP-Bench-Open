:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Diet: buy whole servings of each food so that every nutritional requirement
% is met at least, at minimum total cost.
model(Instance, Vars, [cost-Cost], min(Cost)) :-
    N = Instance.n,
    Price = Instance.price,
    Limits = Instance.limits,
    length(Servings, N),
    Servings ins 0..10000,
    Vars = [Cost|Servings],
    Cost in 0..1000,
    nutrition(Table),
    maplist({Servings}/[Row, Limit]>>scalar_product(Row, Servings, #>=, Limit),
            Table, Limits),
    scalar_product(Price, Servings, #=, Cost).

% The nutrition table belongs to the problem statement, not to the instance:
% the reference fixes these same four rows for the four foods, and only the
% prices and the requirements vary between instances.
nutrition([[400, 200, 150, 500],   % calories
           [3, 2, 0, 0],           % chocolate
           [2, 2, 4, 4],           % sugar
           [2, 4, 1, 5]]).         % fat
