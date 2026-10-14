:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Sports tournament scheduling: n teams (n even) play over n-1 weeks, each week
% in n/2 periods, one match per period. In a match the first team plays at home
% and the second away. Every team plays once a week, every team plays every
% other team, and every team plays at most twice in the same period.
model(Instance, Vars, [home-HomeRows, away-AwayRows]) :-
    NTeams = Instance.n_teams,
    NWeeks is NTeams - 1,
    NPeriods is NTeams // 2,
    NMatches is NTeams * (NTeams - 1) // 2,
    numlist(1, NTeams, Teams),

    % The matches. Match k is the k-th pair of two different teams; each pair
    % can be played either way round. A row of the table is [match, side,
    % home team, away team] where side 0 has the smaller team at home.
    findall(First-Second, (member(First, Teams), member(Second, Teams), First < Second), Pairs),
    findall([Match, Side, Home, Away],
            (   nth1(Match, Pairs, First-Second),
                member([Side, Home, Away], [[0, First, Second], [1, Second, First]])
            ),
            MatchTable),

    % For week w and period p: Matches[w][p] is the match played, Sides[w][p]
    % which way round, and Home[w][p] and Away[w][p] the two teams, so every
    % match has two different teams (the home team is never the away team).
    slots(NWeeks, NPeriods, 1, NMatches, Matches),
    slots(NWeeks, NPeriods, 0, 1, Sides),
    slots(NWeeks, NPeriods, 1, NTeams, HomeRows),
    slots(NWeeks, NPeriods, 1, NTeams, AwayRows),
    maplist(append, [Matches, Sides, HomeRows, AwayRows],
            [FlatMatches, FlatSides, FlatHomes, FlatAways]),
    slot_tuples(FlatMatches, FlatSides, FlatHomes, FlatAways, Tuples),
    tuples_in(Tuples, MatchTable),

    % every team plays once a week
    maplist([Homes, Aways]>>(append(Homes, Aways, Playing), all_distinct(Playing)),
            HomeRows, AwayRows),

    % every team plays each other: there are as many slots as pairs of teams,
    % so no match is played twice
    all_distinct(FlatMatches),

    % every team plays at most twice in the same period (home or away)
    transpose(HomeRows, HomeColumns),
    transpose(AwayRows, AwayColumns),
    maplist({Teams}/[Homes, Aways]>>at_most_twice(Teams, Homes, Aways),
            HomeColumns, AwayColumns),

    % Symmetry breaking (not part of the problem statement). Renaming the
    % teams and reordering the periods does not change whether a schedule is
    % valid, so the first week is fixed to be teams 1 and 2 in period 1, teams
    % 3 and 4 in period 2, and so on.
    HomeRows = [FirstHomes|_],
    AwayRows = [FirstAways|_],
    first_week(FirstHomes, FirstAways, 1),

    % the search picks the matches first, week by week, then which way round
    append(FlatMatches, FlatSides, Vars).

% slots(+Weeks, +Periods, +Low, +High, -Matrix): a Weeks x Periods matrix of
% variables ranging over Low..High.
slots(Weeks, Periods, Low, High, Matrix) :-
    length(Matrix, Weeks),
    maplist({Periods, Low, High}/[Row]>>(length(Row, Periods), Row ins Low..High), Matrix).

% slot_tuples(+Matches, +Sides, +Homes, +Aways, -Tuples): one [match, side, home,
% away] tuple for each slot.
slot_tuples([], [], [], [], []).
slot_tuples([M|Ms], [S|Ss], [H|Hs], [A|As], [[M, S, H, A]|Tuples]) :-
    slot_tuples(Ms, Ss, Hs, As, Tuples).

% at_most_twice(+Teams, +Homes, +Aways): in one period (its home and away teams
% over all weeks) no team appears more than twice.
at_most_twice(Teams, Homes, Aways) :-
    append(Homes, Aways, Playing),
    length(Teams, NTeams),
    length(Counts, NTeams),
    Counts ins 0..2,
    pairs_keys_values(Pairs, Teams, Counts),
    global_cardinality(Playing, Pairs).

% first_week(+Homes, +Aways, +Team): the first week has teams Team and Team+1
% in the first period, Team+2 and Team+3 in the next, and so on.
first_week([], [], _).
first_week([Home|Homes], [Away|Aways], Team) :-
    Next is Team + 1,
    Home in Team..Next,
    Away in Team..Next,
    Following is Team + 2,
    first_week(Homes, Aways, Following).
