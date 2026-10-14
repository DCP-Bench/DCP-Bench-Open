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
    append(Assign, Vars).
