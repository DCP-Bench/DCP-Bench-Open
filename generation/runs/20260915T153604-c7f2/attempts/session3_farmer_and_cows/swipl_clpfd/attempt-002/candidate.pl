:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Farmer and cows: split the herd between the sons so that each gets his
% allotted number of cows and exactly the same amount of milk.
%
% The assignment variables are channelled to a cow-by-son 0/1 matrix.  Posting
% the channelling explicitly - one son per cow, and the son index as a scalar
% product of the row - is what makes the per-son head count and milk total
% propagate; deriving the indicators from reified equalities alone leaves the
% search to enumerate.
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
    numlist(0, Top, SonIndices),

    length(Matrix, NumCows),
    maplist({NumSons}/[Row]>>(length(Row, NumSons), Row ins 0..1), Matrix),
    maplist({SonIndices}/[Row, Cow]>>channel(Row, SonIndices, Cow),
            Matrix, Assignments),

    transpose(Matrix, BySon),
    maplist({MilkPerCow, Share}/[Column, HeadCount]>>
                fair_share(Column, MilkPerCow, Share, HeadCount),
            BySon, CowsPerSon).

% Exactly one son per cow, and the assignment variable is that son's index.
channel(Row, SonIndices, Cow) :-
    sum(Row, #=, 1),
    scalar_product(SonIndices, Row, #=, Cow).

fair_share(Column, MilkPerCow, Share, HeadCount) :-
    sum(Column, #=, HeadCount),
    scalar_product(MilkPerCow, Column, #=, Share).
