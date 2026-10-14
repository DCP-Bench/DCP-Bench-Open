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

    % each pair of golfers meets at most once: they share a group in at most one
    % week. Totals holds, for every pair, the number of weeks they share a group
    % (0 or 1).
    findall(G, between(1, NGolfers, G), Golfers),
    maplist(pair_totals_row(Meets, NGolfers), Golfers, Totals),

    % Implied constraints. They follow from the ones above, and they let the
    % search decide who plays with whom without looking at the group numbers.
    %
    % In a week, a golfer plays with exactly group_size - 1 other golfers.
    PartnersPerWeek is GroupSize - 1,
    maplist(week_partners(PartnersPerWeek, Golfers), Meets),
    % Over all weeks, a golfer plays with n_weeks * (group_size - 1) different
    % other golfers, because no pair meets twice.
    PartnersInTotal is NWeeks * PartnersPerWeek,
    week_partners(PartnersInTotal, Golfers, Totals),
    % Playing in the same group is transitive: if a plays with b and b with c,
    % then a plays with c.
    findall(G1-G2-G3, (between(1, NGolfers, G1), N2 is G1 + 1, between(N2, NGolfers, G2),
                       N3 is G2 + 1, between(N3, NGolfers, G3)), Triples),
    maplist(week_transitive(Triples), Meets),

    % Search: first decide for every week which golfers play together (the 0/1
    % variables, tried with 1 first), then give each group its number. Branching
    % on the group numbers directly tries every renaming of the groups as a
    % different case, which is what makes the plain search fail on the larger
    % instances. This only orders the search; it adds no constraint on Assign.
    append(Meets, MeetRows),
    append(MeetRows, MeetVars),
    append(Totals, TotalVars),
    append(Assign, AssignVars),
    append([MeetVars, TotalVars, AssignVars], Vars).

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

% Row I of the totals: for each golfer J after golfer I, the number of weeks in
% which they play in the same group, which is at most one.
pair_totals_row(Meets, NGolfers, I, Row) :-
    Next is I + 1,
    findall(J, between(Next, NGolfers, J), Js),
    maplist(pair_total(Meets, I), Js, Row).

pair_total(Meets, I, J, Total) :-
    maplist(meet_var_of(I, J), Meets, PairMeets),
    Total in 0..1,
    sum(PairMeets, #=, Total).

meet_var_of(I, J, Rows, Meet) :-
    meet_var(Rows, I, J, Meet).

% Every golfer has Others partners in Rows (the week's rows or the totals).
week_partners(Others, Golfers, Rows) :-
    maplist(golfer_partners(Others, Rows), Golfers).

golfer_partners(Others, Rows, I) :-
    Before is I - 1,
    findall(J, between(1, Before, J), Earlier),
    maplist(meet_var_before(Rows, I), Earlier, WithEarlier),
    nth1(I, Rows, WithLater),
    append(WithEarlier, WithLater, Partners),
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

% Decide the 0/1 variables in order (they come first in Vars), with 1 first.
labeling_options([leftmost, down]).
