:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Mario collects gold: he starts at his house, visits some houses and ends at
% Luigi's house, then the route closes back to Mario's house. Each leg burns
% fuel and Mario has a fuel limit. Pick the route that collects the most gold.
model(Instance, Successors, [s-Successors], max(Gold)) :-
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
    maplist(leg_fuel, ArcFuel, Successors, Fuels),
    sum(Fuels, #=<, FuelLimit),

    % the gold collected is the gold of the houses on the route
    maplist([House, Next, OnRoute]>>(OnRoute #<==> (Next #\= House)),
            Houses, Successors, OnRoutes),
    sum_list(GoldIn, MaxGold),
    Gold in 0..MaxGold,
    scalar_product(GoldIn, OnRoutes, #=, Gold).

% rank_step(+Ranks, +LuigiRank, +Mario, +House, +Next, +Rank): House has the
% given Rank and Next as its successor. A house on the route that is not
% followed by the return to Mario's house is followed by a house one rank
% higher; a house off the route ranks after Luigi's house.
rank_step(Ranks, LuigiRank, Mario, House, Next, Rank) :-
    Index #= Next + 1,
    element(Index, Ranks, NextRank),
    (Next #\= House #/\ Next #\= Mario) #==> NextRank #= Rank + 1,
    Next #\= House #\/ LuigiRank #< Rank.

% leg_fuel(+Row, +Next, -Fuel): fuel for the leg from a house, whose row of the
% fuel table is Row, to its successor Next.
leg_fuel(Row, Next, Fuel) :-
    Index #= Next + 1,
    element(Index, Row, Fuel).
