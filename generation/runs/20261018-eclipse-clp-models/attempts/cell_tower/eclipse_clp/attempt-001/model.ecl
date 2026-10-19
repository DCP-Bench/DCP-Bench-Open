% Cell tower coverage: choose which candidate tower sites to build, within the
% budget, so that the population covered by the built towers is as large as possible.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [build_tower-Build, total_population_covered-Total], max(Total)) :-
    memberchk(budget-Budget, Instance),
    memberchk(cost-Cost, Instance),
    memberchk(delta-Delta, Instance),
    memberchk(population-Pop, Instance),
    length(Cost, NS),
    length(Pop, NR),
    sum(Pop, SumPop),
    % one binary decision per candidate site: build the tower or not
    length(Build, NS),
    Build :: 0..1,
    % one binary flag per region: the region has signal
    length(Cov, NR),
    Cov :: 0..1,
    % a region is covered exactly when at least one built tower reaches it
    cover_regions(1, Cov, Delta, Build),
    % the total cost of the built towers must not exceed the budget
    ( foreach(C0, Cost), foreach(B, Build), foreach(T, CostTerms) do
        T = C0*B
    ),
    Spent #= sum(CostTerms),
    Spent #=< Budget,
    % total population covered by the regions that have signal
    ( foreach(P, Pop), foreach(C, Cov), foreach(T, PopTerms) do
        T = P*C
    ),
    Total :: 0..SumPop,
    Total #= sum(PopTerms),
    append(Build, Cov, Vars).

% walk the regions in order, region R has flag C
cover_regions(_, [], _, _).
cover_regions(R, [C|Cs], Delta, Build) :-
    cover_region(R, Delta, Build, C),
    R1 is R + 1,
    cover_regions(R1, Cs, Delta, Build).

% region R is covered when the sum of the built towers that reach it is at least 1
cover_region(R, Delta, Build, C) :-
    ( foreach(Row, Delta), foreach(B, Build), foreach(T, Terms), param(R) do
        nth1(R, Row, D),
        T = D*B
    ),
    S #= sum(Terms),
    C #= (S #>= 1).
