% ACC basketball schedule (CSPLib 11): a double round-robin timetable for the nine teams of the
% 1997/98 Atlantic Coast Conference. Every team meets every other team twice, once at home and
% once away, over 18 dates, under nine groups of extra constraints.
% Instance: n_teams(N) and n_days(D) give the number of teams and dates; teams and dates are
% counted from 0. Which team is which, the mirroring scheme and the constraints below belong to
% the problem statement for these nine teams and 18 dates.
%
% Output: config(D, T, O): on date D team T plays team O (O = T means T has a bye).
%         where(D, T, S): on date D team T plays at home (0), has a bye (1) or plays away (2).

team(0..N-1) :- n_teams(N).
day(0..D-1) :- n_days(D).

% The nine teams, in the order of the statement.
#const clem = 0.
#const duke = 1.
#const fsu = 2.
#const gt = 3.
#const umd = 4.
#const unc = 5.
#const ncst = 6.
#const uva = 7.
#const wake = 8.

% The three kinds of date for a team.
#const home = 0.
#const bye = 1.
#const away = 2.
status(home;bye;away).

% The second and every later even date (counting dates from 1) is a weekend date: with dates
% counted from 0 these are the odd numbers.
weekend(D) :- day(D), D \ 2 = 1.

1 { config(D,T,O) : team(O) } 1 :- day(D), team(T).
1 { where(D,T,S) : status(S) } 1 :- day(D), team(T).

% A team cannot have different opponents on the same date, and no two teams share an opponent.
:- config(D,T1,O), config(D,T2,O), T1 < T2.

% If team T plays team O, then team O plays team T.
:- config(D,T,O), not config(D,O,T).

% Connect config and where: a team has a bye exactly when it plays itself; when two teams play
% each other, one plays at home and the other away.
:- config(D,T,T), not where(D,T,bye).
:- where(D,T,bye), config(D,T,O), O != T.
:- config(D,T,O), O != T, where(D,T,S), where(D,O,S).

% Double round-robin: each team plays each other team twice, once at home and once away.
:- team(T), team(O), T != O, #count { D : config(D,T,O), where(D,T,home) } != 1.

% 1. Mirroring. The dates are grouped in pairs (1,8), (2,9), (3,12), (4,13), (5,14), (6,15),
% (7,16), (10,17), (11,18) (counted from 1; written from 0 below). In both dates of a pair each
% team plays the same opponent, with home and away exchanged.
mirror(0,7).  mirror(1,8).  mirror(2,11). mirror(3,12). mirror(4,13).
mirror(5,14). mirror(6,15). mirror(9,16). mirror(10,17).
:- mirror(A,B), config(A,T,O), not config(B,T,O).
:- mirror(A,B), where(A,T,S), not where(B,T,2 - S).

% 2. No two final aways. No team plays away on both of the last two dates.
:- n_days(N), team(T), #count { D : where(D,T,away), D >= N - 2 } > 1.

% 3. Home/away/bye patterns, over runs of consecutive dates.
% No team has more than two away matches in a row, nor more than two home matches in a row.
:- n_days(N), team(T), day(D), D + 3 <= N, #count { E : where(E,T,away), E >= D, E < D + 3 } > 2.
:- n_days(N), team(T), day(D), D + 3 <= N, #count { E : where(E,T,home), E >= D, E < D + 3 } > 2.
% No team has more than three away matches or byes in a row.
:- n_days(N), team(T), day(D), D + 4 <= N,
   #count { E : where(E,T,S), S != home, E >= D, E < D + 4 } > 3.
% No team has more than four home matches or byes in a row.
:- n_days(N), team(T), day(D), D + 5 <= N,
   #count { E : where(E,T,S), S != away, E >= D, E < D + 5 } > 4.

% 4. Weekend pattern. Of the nine weekend dates each team plays four at home, four away and
% has one bye.
:- team(T), #count { D : where(D,T,home), weekend(D) } != 4.
:- team(T), #count { D : where(D,T,away), weekend(D) } != 4.
:- team(T), #count { D : where(D,T,bye), weekend(D) } != 1.

% 5. First weekends. Each team has a home match or a bye on at least two of the first five
% weekends.
first_weekend(D) :- weekend(D), #count { E : weekend(E), E < D } < 5.
:- team(T), #count { D : where(D,T,S), S != away, first_weekend(D) } < 2.

% 6. Rival matches. Every team except FSU has a traditional rival.
rival(duke,unc). rival(clem,gt). rival(ncst,wake). rival(umd,uva).
rival(unc,duke). rival(gt,clem). rival(wake,ncst). rival(uva,umd).
% On the last date every team except FSU plays its rival, unless it plays FSU or has a bye.
:- n_days(N), team(T), T != fsu, config(N - 1,T,O), O != T, O != fsu, not rival(T,O).

% 7. Constrained matches. These pairings occur at least once on dates 11 to 18 (dates 10 to 17
% counted from 0).
#const first_late_date = 10.
must_meet_late(wake,unc). must_meet_late(wake,duke). must_meet_late(gt,unc). must_meet_late(gt,duke).
:- must_meet_late(T,O), #count { D : config(D,T,O), D >= first_late_date } < 1.

% 8. Opponent sequence. UNC and Duke are strong opponents (and so is Wake in the second rule).
strong_two(unc;duke).
strong_three(unc;duke;wake).
% No team other than UNC and Duke plays away against UNC and Duke on two consecutive dates.
:- team(T), T != unc, T != duke, day(D), config(D,T,O1), where(D,T,away),
   config(D + 1,T,O2), where(D + 1,T,away), strong_two(O1), strong_two(O2), O1 != O2.
% No team other than UNC, Duke and Wake plays UNC, Duke and Wake on three consecutive dates,
% in any order and at home or away.
:- team(T), not strong_three(T), day(D), config(D,T,O1), config(D + 1,T,O2), config(D + 2,T,O3),
   strong_three(O1), strong_three(O2), strong_three(O3), O1 != O2, O1 != O3, O2 != O3.

% 9. Other constraints.
% UNC plays its rival Duke on the last date and on date 11, and plays Clem on date 2.
:- n_days(N), not config(N - 1,unc,duke).
:- not config(10,unc,duke).
:- not config(1,unc,clem).
% Duke has a bye on date 16.
:- not where(15,duke,bye).
% Wake does not play home on date 17 and has a bye on date 1.
:- where(16,wake,home).
:- not where(0,wake,bye).
% Clem, Duke, UMD and Wake do not play away on the last date.
no_last_away(clem;duke;umd;wake).
:- n_days(N), no_last_away(T), where(N - 1,T,away).
% Clem, FSU, GT and Wake do not play away on the first date.
no_first_away(clem;fsu;gt;wake).
:- no_first_away(T), where(0,T,away).
% Neither FSU nor NC State has a bye on the last date.
no_last_bye(fsu;ncst).
:- n_days(N), no_last_bye(T), where(N - 1,T,bye).
% UNC does not have a bye on the first date.
:- where(0,unc,bye).

#show config/3.
#show where/3.
