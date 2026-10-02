:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Mario collects gold: he starts at his house, visits some houses and ends at
% Luigi's house, then the route closes back to Mario's house. Each leg burns
% fuel and Mario has a fuel limit. Pick the route that collects the most gold.
model(Instance, Choices, [s-Successors], max(Gold)) :-
    N = Instance.nHouses,
    Mario = Instance.marioHouse,            % 0-based house numbers
    Luigi = Instance.luigiHouse,
    FuelLimit = Instance.fuelLimit,
    ArcFuel = Instance.arc_fuel,            % ArcFuel[i][j]: fuel from house i to j
    GoldIn = Instance.goldInHouse,          % gold lying in each house
    Last is N - 1,
    numlist(0, Last, Houses),

    % Successors[i] is the house after house i on the route, or i itself when
    % house i is not on the route.
    length(Successors, N),
    Successors ins 0..Last,
    % every house has a different successor
    all_distinct(Successors),
    % the route ends at Luigi's house and returns to Mario's house
    nth0(Luigi, Successors, LuigiNext),
    LuigiNext #= Mario,

    % How the search picks a successor. For every house the possible successors
    % are listed from the cheapest leg to the dearest, with the house itself
    % (off the route) last. Choices[i] is the place in that list, so trying
    % small places first follows the cheap legs. The fuel of the leg comes with
    % the place. Successors[i] and Fuels[i] are fixed by Choices[i].
    length(Choices, N),
    Choices ins 1..N,
    maplist(leg_options, Houses, ArcFuel, Options),
    maplist([Choice, options(Candidates, Costs), Next, Fuel]>>
                (element(Choice, Candidates, Next), element(Choice, Costs, Fuel)),
            Choices, Options, Successors, Fuels),

    % Rank[i] is the position of house i on the route (an auxiliary): Mario's
    % house comes first and each house after it ranks one higher than the one
    % before. The houses off the route rank after Luigi's house, which stops
    % them forming a separate loop. The ranks follow from Successors, so they
    % are not labelled.
    length(Ranks, N),
    Ranks ins 1..N,
    all_distinct(Ranks),
    nth0(Mario, Ranks, MarioRank),
    MarioRank #= 1,
    nth0(Luigi, Ranks, LuigiRank),
    maplist({Ranks, LuigiRank, Mario}/[House, Next, Rank]>>
                rank_step(Ranks, LuigiRank, Mario, House, Next, Rank),
            Houses, Successors, Ranks),

    % the fuel burnt over all the legs of the route stays within the limit (a
    % house off the route has fuel 0 to itself)
    sum(Fuels, #=<, FuelLimit),

    % the gold collected is the gold of the houses on the route
    maplist([House, Next, OnRoute]>>(OnRoute #<==> (Next #\= House)),
            Houses, Successors, OnRoutes),
    sum_list(GoldIn, MaxGold),
    Gold in 0..MaxGold,
    scalar_product(GoldIn, OnRoutes, #=, Gold).

% leg_options(+House, +FuelRow, -Options): Options is options(Candidates, Costs),
% the houses that can follow House, cheapest leg first and House itself last,
% and the fuel of each leg.
leg_options(House, FuelRow, options(Candidates, Costs)) :-
    findall(Cost-Next,
            (nth0(Next, FuelRow, Cost), Next =\= House),
            Legs),
    keysort(Legs, Cheapest),
    pairs_keys_values(Cheapest, LegCosts, LegNexts),
    nth0(House, FuelRow, StayCost),
    append(LegNexts, [House], Candidates),
    append(LegCosts, [StayCost], Costs).

% rank_step(+Ranks, +LuigiRank, +Mario, +House, +Next, +Rank): House has the
% given Rank and Next as its successor. A house on the route that is not
% followed by the return to Mario's house is followed by a house one rank
% higher; a house off the route ranks after Luigi's house.
rank_step(Ranks, LuigiRank, Mario, House, Next, Rank) :-
    Index #= Next + 1,
    element(Index, Ranks, NextRank),
    (Next #\= House #/\ Next #\= Mario) #==> NextRank #= Rank + 1,
    Next #\= House #\/ LuigiRank #< Rank.
