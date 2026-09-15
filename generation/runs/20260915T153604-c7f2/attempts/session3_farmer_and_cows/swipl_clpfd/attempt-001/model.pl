:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Farmer and cows: split the herd between the sons so that each gets his
% allotted number of cows and exactly the same amount of milk.
model(Instance, Assignments, [cow_assignments-Assignments]) :-
    NumCows = Instance.num_cows,
    NumSons = Instance.num_sons,
    CowsPerSon = Instance.cows_per_son,
    length(Assignments, NumCows),
    Top is NumSons - 1,
    Assignments ins 0..Top,
    % Cow i yields i + 1 units of milk, as the reference lays the herd out.
    numlist(1, NumCows, MilkPerCow),
    sum_list(MilkPerCow, TotalMilk),
    Share is TotalMilk // NumSons,
    numlist(0, Top, Sons),
    maplist({Assignments, MilkPerCow, CowsPerSon, Share}/[Son]>>
                fair_share(Assignments, MilkPerCow, CowsPerSon, Share, Son),
            Sons).

% One indicator per cow says whether this son got it; that drives both his
% head count and his milk total.
fair_share(Assignments, MilkPerCow, CowsPerSon, Share, Son) :-
    maplist({Son}/[Cow, Indicator]>>(Cow #= Son #<==> Indicator),
            Assignments, Indicators),
    nth0(Son, CowsPerSon, HeadCount),
    sum(Indicators, #=, HeadCount),
    scalar_product(MilkPerCow, Indicators, #=, Share).
