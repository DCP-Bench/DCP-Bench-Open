% Social golfers problem (CSPLib 010).
% The golfers play golf once a week, always in groups of a fixed size. Schedule
% the golfers so that no golfer plays in the same group as any other golfer on
% more than one occasion.
% Output assign[i][j] is the group (0-based) of golfer i in week j.

:- lib(ic).
:- lib(ic_global).
:- lib(listut).
:- import alldifferent/1 from ic_global.

model(Instance, Vars, [assign-Rows]) :-
    memberchk(n_weeks-Weeks, Instance),
    memberchk(n_groups-Groups, Instance),
    memberchk(group_size-Size, Instance),
    Golfers is Groups * Size,
    MaxGroup is Groups - 1,
    % One row per golfer, one column per week; each entry is a group number.
    length(Rows, Golfers),
    ( foreach(Row, Rows), param(Weeks, MaxGroup) do
        length(Row, Weeks),
        Row :: 0..MaxGroup
    ),
    flatten(Rows, Vars),
    % Every week, each group holds exactly group_size golfers.
    ( for(J, 1, Weeks), param(Rows, MaxGroup, Size) do
        column(Rows, J, Col),
        ( for(G, 0, MaxGroup), param(Col, Size) do
            occurrences(G, Col, Size)
        )
    ),
    % No two golfers are in the same group in more than one week.
    pair_limits(Rows).

% Smallest domain first, the lowest group first: the search order for the
% golfers' week-by-week assignments.
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Column J (1-based) of the golfer rows: the groups of all golfers in week J.
column(Rows, J, Col) :-
    ( foreach(R, Rows), foreach(X, Col), param(J) do
        nth1(J, R, X)
    ).

% Every pair of golfers shares at most one week in the same group.
pair_limits([]).
pair_limits([R|Rs]) :-
    ( foreach(R2, Rs), param(R) do
        same_group_at_most_once(R, R2)
    ),
    pair_limits(Rs).

same_group_at_most_once(R1, R2) :-
    ( foreach(X, R1), foreach(Y, R2), foreach(B, Bs) do
        B #= (X #= Y)
    ),
    Bs :: 0..1,
    sum(Bs) #=< 1.
