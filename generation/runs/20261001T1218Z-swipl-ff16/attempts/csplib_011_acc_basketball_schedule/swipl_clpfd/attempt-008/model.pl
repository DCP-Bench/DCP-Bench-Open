:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% ACC basketball schedule (1997/98): a double round-robin timetable for nine
% basketball teams over 18 dates, where every team plays every other team once
% at home and once away, subject to the mirroring, home/away pattern, weekend,
% rivalry and other conference rules below.
%
% The schedule is modelled by who hosts whom: Hosts[d][t][u] is 1 when team t
% plays at home against team u on day d. Opponent, home/away/bye and the
% printed Config and Where are all computed from it, which makes "if t plays u
% then u plays t" hold by construction and keeps every rule a sum of 0/1
% values.
model(Instance, Vars, [config-Config, where-Where]) :-
    NTeams = Instance.n_teams,
    NDays = Instance.n_days,
    LastTeam is NTeams - 1,
    LastDay is NDays - 1,
    numlist(0, LastTeam, Teams),

    % The teams and the conventions of the schedule belong to the problem (the
    % teams are the nine ACC teams, numbered as in the problem). Days are
    % counted from 0; the odd days are weekends.
    Clem = 0, Duke = 1, Fsu = 2, Gt = 3, Umd = 4, Unc = 5, Ncst = 6, Uva = 7, Wake = 8,
    Rivals = [Gt, Unc, Fsu, Clem, Uva, Duke, Wake, Umd, Ncst],   % rival of each team; FSU has none

    % 1. Mirroring. The dates are paired up so that each team plays the same
    % team on both dates of a pair, once at home and once away (a bye stays a
    % bye). Nemhauser and Trick's mirroring scheme, as pairs of days. The
    % second day of a pair is the transpose of the first (whoever hosts on
    % one day is the guest on the other), so the two days share variables.
    MirrorPairs = [[0, 7], [1, 8], [2, 11], [3, 12], [4, 13], [5, 14], [6, 15], [9, 16], [10, 17]],
    length(Hosts, NDays),
    length(HomesByDay, NDays),
    length(AwaysByDay, NDays),
    length(ByesByDay, NDays),
    place_pairs(MirrorPairs, NTeams, Hosts, HomesByDay, AwaysByDay, ByesByDay, MeetsByPair, PairVars),
    % Home[d][t], Away[d][t] and Bye[d][t] are 1 when team t plays at home,
    % plays away or does not play on day d: a team plays at most one game a
    % day. On the second day of a pair, home and away swap places.
    transpose(HomesByDay, HomesOf),          % per team: its Home values over the days
    transpose(AwaysByDay, AwaysOf),
    transpose(ByesByDay, ByesOf),

    % Implied: every game has one home team and one away team, so on each day
    % as many teams play at home as play away.
    maplist([Homes, Aways]>>(sum(Homes, #=, Total), sum(Aways, #=, Total)),
            HomesByDay, AwaysByDay),

    % Implied by the rest (stated for propagation): the two days of a pair
    % repeat the same games, so over the nine pairs of days every two teams
    % meet exactly once, and every team has exactly one bye.
    transpose(MeetsByPair, MeetsOfPair),
    maplist([Meets]>>sum(Meets, #=, 1), MeetsOfPair),
    maplist(first_days(MirrorPairs), ByesOf, ByesOnFirstDays),
    maplist([Byes]>>sum(Byes, #=, 1), ByesOnFirstDays),

    % Double round-robin: each team plays each other team twice, once home and
    % once away: team t hosts team u on exactly one day.
    maplist({Hosts, Teams}/[T]>>
                maplist({Hosts, T}/[U]>>
                            (U =:= T -> true
                            ;   (hosts_over_days(Hosts, T, U, Cells), sum(Cells, #=, 1))),
                        Teams),
            Teams),

    % 2. No two final aways: no team plays away on both last dates.
    % 3. Home/away/bye pattern: no team has more than two away matches in a
    % row, more than two home matches in a row, more than three away matches
    % or byes in a row, or more than four home matches or byes in a row.
    % 4. Weekend pattern: of the weekends, each team plays four at home, four
    % away and has one bye.
    % 5. First weekends: each team has home matches or byes on at least two of
    % the first five weekends.
    maplist(team_patterns, HomesOf, AwaysOf, ByesOf),

    % 6. Rival matches: on the last date every team except FSU plays its
    % rival, unless it plays FSU or has a bye.
    maplist({Hosts, LastDay, Fsu, ByesByDay}/[Team, Rival]>>
                (Team =:= Fsu -> true
                ;   (meet(Hosts, LastDay, Team, Rival, MeetsRival),
                     meet(Hosts, LastDay, Team, Fsu, MeetsFsu),
                     nth0(LastDay, ByesByDay, Byes),
                     nth0(Team, Byes, ByeToday),
                     MeetsRival + MeetsFsu + ByeToday #>= 1)),
            Teams, Rivals),

    % 7. Constrained matches: in dates 11 to 18 (days 10 to 17) Wake plays UNC
    % and Duke, and GT plays UNC and Duke, at least once each.
    numlist(10, LastDay, LateDays),
    maplist({Hosts, LateDays}/[Team-Other]>>
                (maplist({Hosts, Team, Other}/[Day, Meets]>>meet(Hosts, Day, Team, Other, Meets),
                         LateDays, MeetsLate),
                 sum(MeetsLate, #>=, 1)),
            [Wake-Unc, Wake-Duke, Gt-Unc, Gt-Duke]),

    % 8. Opponent sequences: no team (other than UNC and Duke) plays away
    % against UNC and Duke on two consecutive dates, in either order; and no
    % team (other than UNC, Duke and Wake) plays UNC, Duke and Wake on three
    % consecutive dates in any order.
    PenultimateDay is LastDay - 1,
    numlist(0, PenultimateDay, PairStarts),
    maplist({Hosts, PairStarts, Unc, Duke}/[Team]>>
                (   ( Team =:= Unc ; Team =:= Duke ) -> true
                ;   maplist({Hosts, Team, Unc, Duke}/[Day]>>consecutive_aways(Hosts, Day, Team, Unc, Duke),
                            PairStarts)
                ),
            Teams),
    TripleLast is LastDay - 2,
    numlist(0, TripleLast, TripleStarts),
    findall([A, B, C], permutation([Unc, Duke, Wake], [A, B, C]), Orders),
    maplist({Hosts, TripleStarts, Orders, Unc, Duke, Wake}/[Team]>>
                (   ( Team =:= Unc ; Team =:= Duke ; Team =:= Wake ) -> true
                ;   maplist({Hosts, Team, Orders}/[Day]>>not_in_a_row(Hosts, Day, Team, Orders),
                            TripleStarts)
                ),
            Teams),

    % 9. Other constraints. (Home 0, bye and away are the three places.)
    meet(Hosts, 10, Unc, Duke, UncDukeEleven), UncDukeEleven #= 1,   % UNC plays Duke in date 11
    meet(Hosts, 17, Unc, Duke, UncDukeLast), UncDukeLast #= 1,       % ... and in the last date
    meet(Hosts, 1, Unc, Clem, UncClem), UncClem #= 1,                % UNC plays Clem in the second date
    entry(ByesByDay, 15, Duke, 1),                                   % Duke has a bye in date 16
    entry(HomesByDay, 16, Wake, 0),                                  % Wake is not at home in date 17
    entry(ByesByDay, 0, Wake, 1),                                    % Wake has a bye in the first date
    maplist({AwaysByDay}/[Team]>>entry(AwaysByDay, 17, Team, 0),
            [Clem, Duke, Umd, Wake]),            % these four are not away in the last date
    maplist({AwaysByDay}/[Team]>>entry(AwaysByDay, 0, Team, 0),
            [Clem, Fsu, Gt, Wake]),              % these four are not away in the first date
    maplist({ByesByDay}/[Team]>>entry(ByesByDay, 17, Team, 0),
            [Fsu, Ncst]),                        % FSU and NCSt have no bye in the last date
    entry(ByesByDay, 0, Unc, 0),                 % UNC has no bye in the first date

    % What is printed. Config[d][t] is the team that team t plays on day d
    % (itself on a bye); Where[d][t] is 0 at home, 1 on a bye and 2 away.
    maplist({Teams}/[Matrix, Byes, ConfigRow]>>day_config(Teams, Matrix, Byes, ConfigRow),
            Hosts, ByesByDay, Config),
    maplist([Aways, Byes, WhereRow]>>
                maplist([Away, Bye, Place]>>(Place #= 2 * Away + Bye), Aways, Byes, WhereRow),
            AwaysByDay, ByesByDay, Where),

    % The search goes through the pairs of days in time order; for each pair it
    % decides which teams meet (who plays whom), then where each team plays
    % (home, away or not at all) on the first day, then who hosts whom.
    append(PairVars, Vars).

% interleave(+Xs, +Ys, -Zs): Zs lists X1, Y1, X2, Y2, ...
interleave([], [], []).
interleave([X|Xs], [Y|Ys], [X, Y|Zs]) :-
    interleave(Xs, Ys, Zs).

% place_pairs(+MirrorPairs, +NTeams, +Hosts, +HomesByDay, +AwaysByDay, +ByesByDay,
%             -MeetsByPair, -PairVars): fill in the hosting matrices of two paired days and
% who is at home, away or off on each of them. MeetsByPair lists, for each pair
% of days, a 0/1 value for every two teams t < u: 1 when they play each other.
place_pairs([], _, _, _, _, _, [], []).
place_pairs([[Day1, Day2]|Pairs], NTeams, Hosts, HomesByDay, AwaysByDay, ByesByDay,
            [Meets|MeetsByPair], [Variables|PairVars]) :-
    host_matrix(NTeams, Matrix),
    transpose(Matrix, Mirrored),
    day_status(Matrix, Homes, Aways, Byes),
    nth0(Day1, Hosts, Matrix),
    nth0(Day2, Hosts, Mirrored),
    nth0(Day1, HomesByDay, Homes),
    nth0(Day2, HomesByDay, Aways),
    nth0(Day1, AwaysByDay, Aways),
    nth0(Day2, AwaysByDay, Homes),
    nth0(Day1, ByesByDay, Byes),
    nth0(Day2, ByesByDay, Byes),
    pair_meets(Matrix, Meets),
    % the variables the search decides for this pair of days
    append(Matrix, HostCells),
    append([Meets, Homes, Aways, HostCells], Variables),
    place_pairs(Pairs, NTeams, Hosts, HomesByDay, AwaysByDay, ByesByDay, MeetsByPair, PairVars).

% pair_meets(+Matrix, -Meets): for every two teams t < u, a 0/1 value that is 1
% when one of them hosts the other (so they play each other).
pair_meets(Matrix, Meets) :-
    length(Matrix, N),
    Last is N - 1,
    numlist(0, Last, Teams),
    findall(T-U, (member(T, Teams), member(U, Teams), T < U), Pairs),
    maplist({Matrix}/[T-U, Meet]>>
                (nth0(T, Matrix, Row), nth0(U, Row, Hosted),
                 nth0(U, Matrix, Row2), nth0(T, Row2, Visited),
                 Meet in 0..1, Meet #= Hosted + Visited),
            Pairs, Meets).

% first_days(+MirrorPairs, +ByDay, -Firsts): the values of a team on the first day
% of each pair of days.
first_days(MirrorPairs, ByDay, Firsts) :-
    maplist({ByDay}/[[Day1, _], Value]>>nth0(Day1, ByDay, Value), MirrorPairs, Firsts).

% host_matrix(+N, -Matrix): Matrix[t][u] is 1 when team t hosts team u; a team
% does not host itself.
host_matrix(N, Matrix) :-
    length(Matrix, N),
    LastTeam is N - 1,
    numlist(0, LastTeam, Teams),
    maplist({N}/[Team, Row]>>(length(Row, N), nth0(Team, Row, 0), Row ins 0..1), Teams, Matrix).

% day_status(+Matrix, -Homes, -Aways, -Byes): for each team, whether it plays at
% home, plays away or has a bye on the day with the given hosting matrix.
day_status(Matrix, Homes, Aways, Byes) :-
    maplist([Row, Home]>>(Home in 0..1, sum(Row, #=, Home)), Matrix, Homes),
    transpose(Matrix, Columns),
    maplist([Column, Away]>>(Away in 0..1, sum(Column, #=, Away)), Columns, Aways),
    maplist([Home, Away, Bye]>>(Bye in 0..1, Bye #= 1 - Home - Away), Homes, Aways, Byes).

% hosts_over_days(+Hosts, +T, +U, -Cells): Cells[d] is 1 when team T hosts team U
% on day d.
hosts_over_days(Hosts, T, U, Cells) :-
    maplist({T, U}/[Matrix, Cell]>>(nth0(T, Matrix, Row), nth0(U, Row, Cell)), Hosts, Cells).

% meet(+Hosts, +Day, +T, +U, -Meets): Meets is 1 when teams T and U play each
% other on the day (either at home).
meet(Hosts, Day, T, U, Meets) :-
    entry_host(Hosts, Day, T, U, Cell1),
    entry_host(Hosts, Day, U, T, Cell2),
    Meets #= Cell1 + Cell2.

% entry(+ByDay, +Day, +Team, +Value): the value for Team on Day is Value.
entry(ByDay, Day, Team, Value) :-
    nth0(Day, ByDay, Row),
    nth0(Team, Row, Value).

% consecutive_aways(+Hosts, +Day, +Team, +Unc, +Duke): Team does not play away at
% UNC on Day and away at Duke the day after, or the other way round.
consecutive_aways(Hosts, Day, Team, Unc, Duke) :-
    Next is Day + 1,
    entry_host(Hosts, Day, Unc, Team, UncHostsToday),
    entry_host(Hosts, Next, Duke, Team, DukeHostsTomorrow),
    UncHostsToday + DukeHostsTomorrow #=< 1,
    entry_host(Hosts, Day, Duke, Team, DukeHostsToday),
    entry_host(Hosts, Next, Unc, Team, UncHostsTomorrow),
    DukeHostsToday + UncHostsTomorrow #=< 1.

% entry_host(+Hosts, +Day, +Host, +Guest, -Cell): 1 when Host plays at home
% against Guest on Day.
entry_host(Hosts, Day, Host, Guest, Cell) :-
    nth0(Day, Hosts, Matrix),
    nth0(Host, Matrix, Row),
    nth0(Guest, Row, Cell).

% not_in_a_row(+Hosts, +Day, +Team, +Orders): over the three days from Day the
% team does not meet UNC, Duke and Wake, in any of the given orders.
not_in_a_row(Hosts, Day, Team, Orders) :-
    Day2 is Day + 1,
    Day3 is Day + 2,
    maplist({Hosts, Day, Day2, Day3, Team}/[[A, B, C]]>>
                (meet(Hosts, Day, Team, A, MeetsA),
                 meet(Hosts, Day2, Team, B, MeetsB),
                 meet(Hosts, Day3, Team, C, MeetsC),
                 MeetsA + MeetsB + MeetsC #=< 2),
            Orders).

% team_patterns(+Homes, +Aways, +Byes): the home/away/bye rules for one team,
% whose Home, Away and Bye values on each day are listed.
team_patterns(Homes, Aways, Byes) :-
    % no two final aways
    append(_, [SecondLast, Last], Aways),
    SecondLast + Last #=< 1,
    % at most two home matches and at most two away matches in any three days
    windows(3, Homes, HomeThrees),
    maplist([Window]>>sum(Window, #=<, 2), HomeThrees),
    windows(3, Aways, AwayThrees),
    maplist([Window]>>sum(Window, #=<, 2), AwayThrees),
    % at most three away matches or byes in any four days
    maplist([Away, Bye, Both]>>(Both #= Away + Bye), Aways, Byes, AwayOrBye),
    windows(4, AwayOrBye, Fours),
    maplist([Window]>>sum(Window, #=<, 3), Fours),
    % at most four home matches or byes in any five days
    maplist([Home, Bye, Both]>>(Both #= Home + Bye), Homes, Byes, HomeOrBye),
    windows(5, HomeOrBye, Fives),
    maplist([Window]>>sum(Window, #=<, 4), Fives),
    % weekends are the odd days: four home, four away and one bye
    odd_days(Homes, WeekendHomes),
    odd_days(Aways, WeekendAways),
    odd_days(Byes, WeekendByes),
    sum(WeekendHomes, #=, 4),
    sum(WeekendAways, #=, 4),
    sum(WeekendByes, #=, 1),
    % at least two home matches or byes on the first five weekends
    length(FirstHomes, 5), append(FirstHomes, _, WeekendHomes),
    length(FirstByes, 5), append(FirstByes, _, WeekendByes),
    append(FirstHomes, FirstByes, HomeOrByeEarly),
    sum(HomeOrByeEarly, #>=, 2).

% windows(+Size, +List, -Windows): every Size consecutive entries of List.
windows(Size, List, []) :-
    length(List, Length),
    Length < Size,
    !.
windows(Size, [X|Xs], [Window|Windows]) :-
    length(Window, Size),
    append(Window, _, [X|Xs]),
    windows(Size, Xs, Windows).

% odd_days(+List, -Odds): the entries of List at positions 1, 3, 5, ... counted
% from 0 (the weekends).
odd_days([_, Odd|Rest], [Odd|Odds]) :-
    !,
    odd_days(Rest, Odds).
odd_days(_, []).

% day_config(+Teams, +Matrix, +Byes, -ConfigRow): ConfigRow[t] is the number of
% the team that team t plays on a day with hosting matrix Matrix: the sum of
% the numbers of the teams it hosts and visits, or t itself on a bye.
day_config(Teams, Matrix, Byes, ConfigRow) :-
    transpose(Matrix, Columns),
    config_row(Teams, Matrix, Columns, Byes, Teams, ConfigRow).

config_row([], [], [], [], _, []).
config_row([T|Ts], [Row|Rows], [Column|Columns], [Bye|Byes], Teams, [Value|Values]) :-
    append([Row, Column, [Bye]], Terms),
    append([Teams, Teams, [T]], Coefficients),
    scalar_product(Coefficients, Terms, #=, Value),
    config_row(Ts, Rows, Columns, Byes, Teams, Values).
