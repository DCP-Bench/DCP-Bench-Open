:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Farmer and cows: split the herd between the sons so that each gets his
% allotted number of cows and exactly the same amount of milk.
%
% Two things make this solvable inside the budget.  The assignment variables
% are channelled to a cow-by-son 0/1 matrix, so the per-son head count and
% milk total are plain sums over a column rather than sums over reified
% equalities.  And the cows are labelled heaviest first: the biggest yields
% are what pin the milk balance down, so deciding them early prunes far more
% than the default order does.
model(Instance, Vars, [cow_assignments-Assignments]) :-
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
    numlist(0, Top, SonIndices),

    length(Matrix, NumCows),
    maplist({NumSons}/[Row]>>(length(Row, NumSons), Row ins 0..1), Matrix),
    maplist({SonIndices}/[Row, Cow]>>channel(Row, SonIndices, Cow),
            Matrix, Assignments),

    transpose(Matrix, BySon),
    maplist({MilkPerCow, Share}/[Column, HeadCount]>>
                fair_share(Column, MilkPerCow, Share, HeadCount),
            BySon, CowsPerSon),

    reverse(Assignments, Heaviest),
    append(Matrix, MatrixVars),
    append(Heaviest, MatrixVars, Vars).

% Exactly one son per cow, and the assignment variable is that son's index.
channel(Row, SonIndices, Cow) :-
    sum(Row, #=, 1),
    scalar_product(SonIndices, Row, #=, Cow).

fair_share(Column, MilkPerCow, Share, HeadCount) :-
    sum(Column, #=, HeadCount),
    scalar_product(MilkPerCow, Column, #=, Share).

% Label in the order given above rather than by smallest domain: every
% assignment variable has the same domain size, so first-fail has nothing to
% go on here.
labeling_options([leftmost]).
