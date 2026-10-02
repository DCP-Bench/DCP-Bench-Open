:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Social golfers: n_groups * group_size golfers play once a week for n_weeks, in
% n_groups groups of group_size, so that no two golfers are in the same group
% in more than one week.
model(Instance, Vars, [assign-Assign]) :-
    NWeeks = Instance.n_weeks,
    NGroups = Instance.n_groups,
    GroupSize = Instance.group_size,

    NGolfers is NGroups * GroupSize,
    Top is NGroups - 1,
    % Assign[g][w] = the group (numbered from 0) golfer g plays in during week w
    length(Assign, NGolfers),
    maplist({NWeeks, Top}/[Row]>>(length(Row, NWeeks), Row ins 0..Top), Assign),

    % each group has exactly group_size players in every week (each week is a
    % column of Assign)
    numlist(0, Top, Groups),
    pairs_keys_values(Counts, Groups, GroupSizes),
    length(GroupSizes, NGroups),
    maplist(=(GroupSize), GroupSizes),
    transpose(Assign, Weeks),
    maplist({Counts}/[Week]>>global_cardinality(Week, Counts), Weeks),

    % each pair of golfers meets at most once: they share a group in at most one week
    findall(G1-G2, (between(1, NGolfers, G1), Next is G1 + 1, between(Next, NGolfers, G2)), Pairs),
    maplist({Assign}/[G1-G2]>>(
                nth1(G1, Assign, Row1), nth1(G2, Assign, Row2),
                maplist([A, B, Meet]>>(Meet #<==> (A #= B)), Row1, Row2, Meets),
                sum(Meets, #=<, 1)),
            Pairs),

    % Symmetry breaking (any schedule can be renamed to satisfy it, so no
    % schedule is lost). Golfers and groups are interchangeable, so in the first
    % week the golfers fill the groups in order: golfer g plays in group
    % g // group_size ...
    Weeks = [FirstWeek|LaterWeeks],
    LastGolfer is NGolfers - 1,
    numlist(0, LastGolfer, Golfers),
    maplist({GroupSize}/[Golfer, Group]>>(Group #= Golfer // GroupSize), Golfers, FirstWeek),
    % ... and in every later week the groups are numbered in order of their
    % first golfer: a golfer's group is at most one above the highest group
    % number among the golfers before him or her.
    maplist(groups_in_order, LaterWeeks),
    % weeks are listed one after the other in Vars, so the search settles week
    % by week
    append(Weeks, Vars).

% The first golfer plays in group 0 and each next golfer in a group no higher than
% one above the highest one used so far.
groups_in_order([First|Rest]) :-
    First #= 0,
    foldl([Group, Highest0, Highest]>>(Group #=< Highest0 + 1, Highest #= max(Highest0, Group)),
          Rest, 0, _).

% Fill the weeks in order, golfer by golfer; the smallest-domain rule does not
% finish on the larger instances.
labeling_options([leftmost]).
