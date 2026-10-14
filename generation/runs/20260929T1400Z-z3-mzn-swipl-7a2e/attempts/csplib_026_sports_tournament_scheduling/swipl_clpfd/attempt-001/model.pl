:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Sports tournament scheduling: n teams play over n-1 weeks, each week has n/2
% periods, and a period holds one match (a home team and an away team). Every
% team plays once a week, at most twice in the same period over the whole
% tournament, and meets every other team. Teams are numbered 1..n.
model(Instance, Vars, [home-Home, away-Away]) :-
    NTeams = Instance.n_teams,
    NWeeks is NTeams - 1,
    NPeriods is NTeams // 2,

    % Home[w][p], Away[w][p] = the team number in the slot
    length(Home, NWeeks),
    maplist({NPeriods, NTeams}/[Row]>>(length(Row, NPeriods), Row ins 1..NTeams), Home),
    length(Away, NWeeks),
    maplist({NPeriods, NTeams}/[Row]>>(length(Row, NPeriods), Row ins 1..NTeams), Away),
    append(Home, HomeCells),
    append(Away, AwayCells),

    % a team does not play itself
    maplist([H, A]>>(H #\= A), HomeCells, AwayCells),

    % every team plays exactly once a week: the n slots of a week (home and away,
    % all periods) hold n different teams
    maplist([HomeRow, AwayRow]>>(append(HomeRow, AwayRow, Week), all_distinct(Week)), Home, Away),

    % every team meets every other team at least once, at home or away
    findall(T1-T2, (between(1, NTeams, T1), T1p is T1 + 1, between(T1p, NTeams, T2)), Pairs),
    maplist({HomeCells, AwayCells}/[T1-T2]>>(
                maplist({T1, T2}/[H, A, Met]>>(Met #<==> ((H #= T1 #/\ A #= T2) #\/ (H #= T2 #/\ A #= T1))),
                        HomeCells, AwayCells, Meetings),
                sum(Meetings, #>=, 1)), Pairs),

    % a team plays at most twice in the same period over the tournament
    transpose(Home, HomePeriods),
    transpose(Away, AwayPeriods),
    numlist(1, NTeams, Teams),
    maplist({HomePeriods, AwayPeriods}/[T]>>(
                maplist({T}/[HomePeriod, AwayPeriod]>>(
                            maplist({T}/[H, A, Plays]>>(Plays #<==> (H #= T #\/ A #= T)), HomePeriod, AwayPeriod, Played),
                            sum(Played, #=<, 2)), HomePeriods, AwayPeriods)), Teams),
    append(HomeCells, AwayCells, Vars).
