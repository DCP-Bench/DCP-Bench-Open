:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Farmer and cows: split the herd between the sons so that each gets his
% allotted number of cows and exactly the same amount of milk.
%
% The model decides a cow-by-son 0/1 matrix and channels it to the declared
% assignment variables.  Two details matter for search.
%
% The matrix is what gets labelled, heaviest cow first, and the assignments
% follow it.  Labelling the assignments instead does not work: given
% sum(Row) #= 1 and sum(k * Row_k) #= Son, fixing Son does not narrow the row
% by bounds reasoning alone - every row still looks possible - so the per-son
% head count and milk total stay dormant until the very end of the search.
% Deciding the booleans updates both column sums immediately.
%
% Heaviest first, because the largest yields are what pin the milk balance
% down; first-fail has nothing to go on when every variable is a Boolean.
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

    reverse(Matrix, Heaviest),
    append(Heaviest, HeaviestVars),
    append(HeaviestVars, Assignments, Vars).

% Exactly one son per cow, and the assignment variable is that son's index.
channel(Row, SonIndices, Cow) :-
    sum(Row, #=, 1),
    scalar_product(SonIndices, Row, #=, Cow).

fair_share(Column, MilkPerCow, Share, HeadCount) :-
    sum(Column, #=, HeadCount),
    scalar_product(MilkPerCow, Column, #=, Share).

labeling_options([leftmost]).
