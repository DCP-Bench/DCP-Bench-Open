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

    % Meets[w] holds, for every pair of golfers, a 0/1 variable that is 1 when
    % the two play in the same group in week w
    maplist(week_meetings, Weeks, Meets),

    % each pair of golfers meets at most once: they share a group in at most one week
    findall(G1-G2, (between(1, NGolfers, G1), Next is G1 + 1, between(Next, NGolfers, G2)), Pairs),
    maplist(pair_meets_at_most_once(Meets), Pairs),

    % Implied constraints. They follow from the ones above, and they let the
    % search decide who plays with whom without looking at the group numbers.
    %
    % In a week, a golfer plays with exactly group_size - 1 other golfers.
    findall(G, between(1, NGolfers, G), Golfers),
    maplist(week_partners(GroupSize, Golfers), Meets),
    % Playing in the same group is transitive: if a plays with b and b with c,
    % then a plays with c.
    findall(G1-G2-G3, (between(1, NGolfers, G1), N2 is G1 + 1, between(N2, NGolfers, G2),
                       N3 is G2 + 1, between(N3, NGolfers, G3)), Triples),
    maplist(week_transitive(Triples), Meets),

    % Search: first decide for every week which golfers play together (the 0/1
    % variables, tried with 0 first), then give each group its number. Branching
    % on the group numbers directly tries every renaming of the groups as a
    % different case, which is what makes the plain search fail on the larger
    % instances. This only orders the search; it adds no constraint on Assign.
    append(Meets, MeetRows),
    append(MeetRows, MeetVars),
    append(Assign, AssignVars),
    append(MeetVars, AssignVars, Vars).

% The 0/1 variables of one week, as rows: row i has one variable for each golfer
% after golfer i, 1 when that golfer is in the same group as golfer i.
week_meetings([], []).
week_meetings([Group|Later], [Row|Rows]) :-
    maplist({Group}/[Other, Meet]>>(Meet #<==> (Group #= Other)), Later, Row),
    week_meetings(Later, Rows).

% The variable for golfers I < J in one week.
meet_var(Rows, I, J, Meet) :-
    nth1(I, Rows, Row),
    K is J - I,
    nth1(K, Row, Meet).

% Golfers I and J play in the same group in at most one of the weeks.
pair_meets_at_most_once(Meets, I-J) :-
    maplist(meet_var_of(I, J), Meets, PairMeets),
    sum(PairMeets, #=<, 1).

meet_var_of(I, J, Rows, Meet) :-
    meet_var(Rows, I, J, Meet).

% In one week every golfer has group_size - 1 partners.
week_partners(GroupSize, Golfers, Rows) :-
    maplist(golfer_partners(GroupSize, Rows), Golfers).

golfer_partners(GroupSize, Rows, I) :-
    Before is I - 1,
    findall(J, between(1, Before, J), Earlier),
    maplist(meet_var_before(Rows, I), Earlier, WithEarlier),
    nth1(I, Rows, WithLater),
    append(WithEarlier, WithLater, Partners),
    Others is GroupSize - 1,
    sum(Partners, #=, Others).

meet_var_before(Rows, I, J, Meet) :-
    meet_var(Rows, J, I, Meet).

% In one week, of three golfers the pairs that play together are never exactly two.
week_transitive(Triples, Rows) :-
    maplist(not_two_of_three(Rows), Triples).

not_two_of_three(Rows, I-J-K) :-
    meet_var(Rows, I, J, IJ),
    meet_var(Rows, J, K, JK),
    meet_var(Rows, I, K, IK),
    IJ + JK + IK #\= 2.

% Decide the 0/1 variables in order (they come first in Vars), with 0 first.
labeling_options([leftmost, up]).
