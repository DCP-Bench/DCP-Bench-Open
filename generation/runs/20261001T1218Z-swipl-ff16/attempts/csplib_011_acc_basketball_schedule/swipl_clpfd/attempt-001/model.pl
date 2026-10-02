:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% ACC basketball schedule (1997/98): a double round-robin timetable for nine
% basketball teams over 18 dates, where every team plays every other team once
% at home and once away, subject to the mirroring, home/away pattern, weekend,
% rivalry and other conference rules below.
model(Instance, Vars, [config-Config, where-Where]) :-
    NTeams = Instance.n_teams,
    NDays = Instance.n_days,
    LastTeam is NTeams - 1,
    numlist(0, LastTeam, Teams),

    % The teams, and the conventions of the schedule, belong to the problem
    % (the teams are the nine ACC teams, numbered as in the problem).
    Clem = 0, Duke = 1, Fsu = 2, Gt = 3, Umd = 4, Unc = 5, Ncst = 6, Uva = 7, Wake = 8,
    Rivals = [Gt, Unc, Fsu, Clem, Uva, Duke, Wake, Umd, Ncst],   % rival of each team; FSU has none
    Home = 0, Bye = 1, Away = 2,

    % Config[d][t] is the team that team t plays on day d (itself on a bye),
    % and Where[d][t] whether team t plays at home (0), has a bye (1) or plays
    % away (2). Days are counted from 0; odd days are weekends.
    length(Config, NDays),
    maplist({NTeams, LastTeam}/[Row]>>(length(Row, NTeams), Row ins 0..LastTeam), Config),
    length(Where, NDays),
    maplist({NTeams}/[Row]>>(length(Row, NTeams), Row ins 0..2), Where),

    % A team cannot have different opponents on the same day; if team i plays
    % team j then team j plays team i; when two teams play each other, one is
    % at home and the other away; a team plays itself on a bye.
    maplist({Teams}/[ConfigRow, WhereRow]>>day_rules(Teams, ConfigRow, WhereRow),
            Config, Where),

    % The same, team by team: the opponents and the places of team t over the
    % days.
    transpose(Config, OpponentsOf),
    transpose(Where, PlacesOf),

    % Double round-robin: each team plays each other team twice, once home and
    % once away: exactly one day where it plays that opponent at home.
    maplist({Teams, Home}/[Team, Opponents, Places]>>
                maplist({Team, Opponents, Places, Home}/[Other]>>
                            (Other =:= Team -> true ; hosts_once(Opponents, Places, Other, Home)),
                        Teams),
            Teams, OpponentsOf, PlacesOf),

    % 1. Mirroring. The dates are paired up so that each team plays the same
    % team on both dates of a pair, once at home and once away (a bye stays a
    % bye). Nemhauser and Trick's mirroring scheme: day d is paired with
    % Scheme[d].
    Scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10],
    mirror(Scheme, 0, Config, Where),

    % 2. No two final aways: no team plays away on both last dates.
    % 3. Home/away/bye pattern: no team has more than two away matches in a
    % row, more than two home matches in a row, more than three away matches
    % or byes in a row, or more than four home matches or byes in a row.
    % 4. Weekend pattern: of the weekends, each team plays four at home, four
    % away and has one bye.
    % 5. First weekends: each team has home matches or byes on at least two of
    % the first five weekends.
    maplist({Home, Bye, Away}/[Places]>>team_patterns(Places, Home, Bye, Away), PlacesOf),

    % 6. Rival matches: on the last date every team except FSU plays its
    % rival, unless it plays FSU or has a bye.
    last_day(Config, LastOpponents),
    last_day(Where, LastPlaces),
    maplist({Fsu, Bye}/[Team, Rival, Opponent, Place]>>
                (Team =:= Fsu -> true
                ;   (Opponent #= Rival #\/ Opponent #= Fsu #\/ Place #= Bye)),
            Teams, Rivals, LastOpponents, LastPlaces),

    % 7. Constrained matches: in dates 11 to 18 (days 10 to 17) Wake plays UNC
    % and Duke, and GT plays UNC and Duke, at least once each.
    maplist({OpponentsOf}/[Team-Other]>>
                (nth0(Team, OpponentsOf, Opponents),
                 length(Early, 10), append(Early, Late, Opponents),
                 plays_at_least_once(Late, Other)),
            [Wake-Unc, Wake-Duke, Gt-Unc, Gt-Duke]),

    % 8. Opponent sequences: no team (other than UNC and Duke) plays away
    % against UNC and Duke on two consecutive dates, in either order; and no
    % team (other than UNC, Duke and Wake) plays UNC, Duke and Wake on three
    % consecutive dates in any order.
    maplist({Unc, Duke, Wake}/[Team, Opponents, Places]>>
                opponent_sequences(Team, Opponents, Places, Unc, Duke, Wake),
            Teams, OpponentsOf, PlacesOf),

    % 9. Other constraints.
    cell(Config, 10, Unc, Duke),                   % UNC plays Duke in date 11
    cell(Config, 17, Unc, Duke),                   % ... and in the last date
    cell(Config, 1, Unc, Clem),                    % UNC plays Clem in the second date
    cell(Where, 15, Duke, Bye),                    % Duke has a bye in date 16
    cell(Where, 16, Wake, Place17), Place17 #\= Home,   % Wake is not at home in date 17
    cell(Where, 0, Wake, Bye),                     % Wake has a bye in the first date
    maplist({Where, Away}/[Team]>>(cell(Where, 17, Team, Place), Place #\= Away),
            [Clem, Duke, Umd, Wake]),              % these four are not away in the last date
    maplist({Where, Away}/[Team]>>(cell(Where, 0, Team, Place), Place #\= Away),
            [Clem, Fsu, Gt, Wake]),                % these four are not away in the first date
    maplist({Where, Bye}/[Team]>>(cell(Where, 17, Team, Place), Place #\= Bye),
            [Fsu, Ncst]),                          % FSU and NCSt have no bye in the last date
    cell(Where, 0, Unc, FirstPlace), FirstPlace #\= Bye,   % UNC has no bye in the first date

    append(Config, ConfigCells),
    append(Where, WhereCells),
    append(ConfigCells, WhereCells, Vars).

% day_rules(+Teams, +ConfigRow, +WhereRow): the rules for one day.
day_rules(Teams, ConfigRow, WhereRow) :-
    all_distinct(ConfigRow),
    maplist(team_rules(ConfigRow, WhereRow), Teams, ConfigRow, WhereRow).

% team_rules(+ConfigRow, +WhereRow, +Team, +Opponent, +Place): Team plays
% Opponent at Place; the opponent plays Team back, at the opposite place.
team_rules(ConfigRow, WhereRow, Team, Opponent, Place) :-
    Index #= Opponent + 1,
    element(Index, ConfigRow, Team),
    element(Index, WhereRow, OpponentPlace),
    (Place #= 0) #<==> (Opponent #\= Team #/\ OpponentPlace #= 2),
    (Place #= 2) #<==> (Opponent #\= Team #/\ OpponentPlace #= 0),
    (Place #= 1) #<==> (Opponent #= Team).

% hosts_once(+Opponents, +Places, +Other, +Home): over the days, the team plays
% Other at home on exactly one.
hosts_once(Opponents, Places, Other, Home) :-
    maplist({Other, Home}/[Opponent, Place, Flag]>>(Flag #<==> (Opponent #= Other #/\ Place #= Home)),
            Opponents, Places, Flags),
    sum(Flags, #=, 1).

% mirror(+Scheme, +Day, +Config, +Where): day Day plays the same opponents as
% its partner Scheme[Day], at the opposite places.
mirror([], _, _, _).
mirror([Partner|Partners], Day, Config, Where) :-
    (   Partner > Day
    ->  nth0(Day, Config, Row),
        nth0(Partner, Config, Row),
        nth0(Day, Where, Places),
        nth0(Partner, Where, PartnerPlaces),
        maplist([Place, PartnerPlace]>>(Place #= 2 - PartnerPlace), Places, PartnerPlaces)
    ;   true
    ),
    Next is Day + 1,
    mirror(Partners, Next, Config, Where).

% team_patterns(+Places, +Home, +Bye, +Away): the home/away/bye rules for one
% team, whose place on each day is listed in Places.
team_patterns(Places, Home, Bye, Away) :-
    % no two final aways
    append(_, [SecondLast, Last], Places),
    #\ (SecondLast #= Away #/\ Last #= Away),
    % at most two home matches and at most two away matches in any three days
    windows(3, Places, Threes),
    maplist({Home, Away}/[Window]>>(at_most(Window, Home, Home, 2), at_most(Window, Away, Away, 2)),
            Threes),
    % at most three away matches or byes in any four days
    windows(4, Places, Fours),
    maplist({Bye, Away}/[Window]>>at_most(Window, Bye, Away, 3), Fours),
    % at most four home matches or byes in any five days
    windows(5, Places, Fives),
    maplist({Home, Bye}/[Window]>>at_most(Window, Home, Bye, 4), Fives),
    % weekends are the odd days: four home, four away and one bye
    odd_days(Places, Weekends),
    global_cardinality(Weekends, [Home-4, Bye-1, Away-4]),
    % at least two home matches or byes on the first five weekends
    length(FirstFive, 5),
    append(FirstFive, _, Weekends),
    maplist({Home, Bye}/[Place, Flag]>>(Flag #<==> (Place in Home..Bye)), FirstFive, Flags),
    sum(Flags, #>=, 2).

% windows(+Size, +List, -Windows): every Size consecutive entries of List.
windows(Size, List, []) :-
    length(List, Length),
    Length < Size,
    !.
windows(Size, [X|Xs], [Window|Windows]) :-
    length(Window, Size),
    append(Window, _, [X|Xs]),
    windows(Size, Xs, Windows).

% at_most(+Window, +Low, +High, +Max): at most Max entries of Window lie in
% Low..High (places are numbered home 0, bye 1, away 2).
at_most(Window, Low, High, Max) :-
    maplist({Low, High}/[Place, Flag]>>(Flag #<==> (Place in Low..High)), Window, Flags),
    sum(Flags, #=<, Max).

% odd_days(+List, -Odds): the entries of List at positions 1, 3, 5, ... counted
% from 0 (the weekends).
odd_days([_, Odd|Rest], [Odd|Odds]) :-
    !,
    odd_days(Rest, Odds).
odd_days(_, []).

% last_day(+Matrix, -Last): the last row of the matrix.
last_day(Matrix, Last) :-
    append(_, [Last], Matrix).

% plays_at_least_once(+Opponents, +Other): Other is among the Opponents.
plays_at_least_once(Opponents, Other) :-
    maplist({Other}/[Opponent, Flag]>>(Flag #<==> (Opponent #= Other)), Opponents, Flags),
    sum(Flags, #>=, 1).

% opponent_sequences(+Team, +Opponents, +Places, +Unc, +Duke, +Wake): the
% opponent sequence rules for one team.
opponent_sequences(Team, Opponents, Places, Unc, Duke, Wake) :-
    (   ( Team =:= Unc ; Team =:= Duke )
    ->  true
    ;   pairs_of_days(Opponents, Places, Pairs),
        maplist({Unc, Duke}/[[Opponent1, Place1, Opponent2, Place2]]>>
                    ( #\ (Opponent1 #= Unc #/\ Place1 #= 2 #/\ Opponent2 #= Duke #/\ Place2 #= 2),
                      #\ (Opponent1 #= Duke #/\ Place1 #= 2 #/\ Opponent2 #= Unc #/\ Place2 #= 2) ),
                Pairs)
    ),
    (   ( Team =:= Unc ; Team =:= Duke ; Team =:= Wake )
    ->  true
    ;   windows(3, Opponents, Triples),
        maplist({Unc, Duke, Wake}/[Triple]>>not_all_three(Triple, [Unc, Duke, Wake]), Triples)
    ).

% pairs_of_days(+Opponents, +Places, -Pairs): for every two consecutive days,
% [opponent, place, next opponent, next place].
pairs_of_days([O1, O2|Opponents], [P1, P2|Places], [[O1, P1, O2, P2]|Pairs]) :-
    !,
    pairs_of_days([O2|Opponents], [P2|Places], Pairs).
pairs_of_days(_, _, []).

% not_all_three(+Triple, +Teams): the three opponents of three consecutive days
% are not the three Teams in any order.
not_all_three([O1, O2, O3], Teams) :-
    findall([A, B, C], permutation(Teams, [A, B, C]), Orders),
    maplist({O1, O2, O3}/[[A, B, C]]>>( #\ (O1 #= A #/\ O2 #= B #/\ O3 #= C) ), Orders).

% cell(+Matrix, +Day, +Team, ?Value): the entry of the matrix for Team on Day.
cell(Matrix, Day, Team, Value) :-
    nth0(Day, Matrix, Row),
    nth0(Team, Row, Value).
