:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Cell tower siting: build towers within budget so as to cover the largest
% population.  A region counts as covered only if some built site reaches it.
model(Instance, Vars, [build_tower-Build, total_population_covered-Total],
      max(Total)) :-
    Delta = Instance.delta,
    Cost = Instance.cost,
    Population = Instance.population,
    Budget = Instance.budget,
    length(Cost, Sites),
    length(Population, Regions),
    length(Build, Sites),
    Build ins 0..1,
    length(Covered, Regions),
    Covered ins 0..1,
    sum_list(Population, PopulationTotal),
    Total in 0..PopulationTotal,
    append([[Total], Build, Covered], Vars),
    % Reach per region is read down a column of delta, so transpose first.
    transpose(Delta, ByRegion),
    maplist({Build}/[Reaches, C]>>reachable(Build, Reaches, C),
            ByRegion, Covered),
    scalar_product(Cost, Build, #=<, Budget),
    scalar_product(Population, Covered, #=, Total).

reachable(Build, Reaches, Covered) :-
    scalar_product(Reaches, Build, #>=, Covered).
