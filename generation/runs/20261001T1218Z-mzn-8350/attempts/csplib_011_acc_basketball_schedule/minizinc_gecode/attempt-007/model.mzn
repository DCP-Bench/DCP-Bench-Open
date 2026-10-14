% ACC basketball schedule (CSPLib 11): a timetable for the 1997/98 Atlantic Coast
% Conference. The 9 teams play a double round-robin (each team plays every other
% team once at home and once away) over 18 dates, subject to nine groups of
% additional constraints (mirroring, final dates, home/away/bye patterns,
% weekends, rivals, constrained matches, opponent sequences and others).
% The teams, the mirroring scheme and the rest of the constraints are fixed by the
% problem statement (they are for exactly 9 teams and 18 dates); the instance only
% gives those two sizes.
include "globals.mzn";

int: n_teams;  % 9
int: n_days;   % 18 dates; day 0 is the first date (a weekday), odd days are weekends

constraint assert(n_teams = 9 /\ n_days = 18, "the constraints are those of the 9-team, 18-date ACC problem");

set of int: Teams = 0..n_teams - 1;
set of int: Days = 0..n_days - 1;

% The nine teams (numbering fixed by the problem statement)
int: CLEM = 0; int: DUKE = 1; int: FSU = 2; int: GT = 3; int: UMD = 4;
int: UNC = 5; int: NCSt = 6; int: UVA = 7; int: WAKE = 8;

% The values of venue[d, t]
int: HOME = 0; int: BYE = 1; int: AWAY = 2;

% rival[t] = the traditional rival of team t: Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA
% (FSU has none and is listed as its own rival)
array[Teams] of int: rival = array1d(Teams, [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]);

% config[d, t] = j iff team t plays team j on date d; config[d, t] = t means a bye
array[Days, Teams] of var Teams: config;
% venue[d, t] = whether team t plays at home (0), has a bye (1) or plays away (2) on date d
array[Days, Teams] of var 0..2: venue;

% a team cannot have different opponents on the same day: on a date all opponents differ
constraint forall(d in Days) (all_different([config[d, t] | t in Teams]));

% if team t plays team j on a date, then team j plays team t
constraint forall(d in Days, t in Teams) (config[d, config[d, t]] = t);

% connect config and venue: when two teams play each other one is at home and
% the other away, and a team has a bye exactly when it is its own opponent
constraint forall(d in Days, t in Teams) (
    (venue[d, t] = HOME <-> (config[d, t] != t /\ venue[d, config[d, t]] = AWAY)) /\
    (venue[d, t] = AWAY <-> (config[d, t] != t /\ venue[d, config[d, t]] = HOME)) /\
    (venue[d, t] = BYE <-> config[d, t] = t));

% Double round-robin: each team plays each other team twice, once at home and once away
constraint forall(t in Teams, opponent in Teams where t != opponent)
    (sum(d in Days) (bool2int(config[d, t] = opponent /\ venue[d, t] = HOME)) = 1);

% Implied (it follows from the double round-robin and the bye definition, but Gecode
% does not derive it): every team meets each other team on exactly two dates, and
% so has n_days - 2*(n_teams - 1) byes
constraint forall(t in Teams)
    (global_cardinality([config[d, t] | d in Days], [j | j in Teams],
                        [if j = t then n_days - 2 * (n_teams - 1) else 2 endif | j in Teams]));

% More implied constraints (every solution satisfies them; Gecode does not derive them).
% Each team has 2*(n_teams-1) = 16 games, 8 at home and 8 away, and 2 byes. Each date has n_teams
% teams, an odd number, and there are 2 byes per team on n_days dates, so every date has
% exactly one bye and the other teams play in pairs, one at home and one away.
constraint forall(t in Teams) (
    sum(d in Days) (bool2int(venue[d, t] = HOME)) = n_teams - 1 /\ sum(d in Days) (bool2int(venue[d, t] = AWAY)) = n_teams - 1 /\ sum(d in Days) (bool2int(venue[d, t] = BYE)) = n_days - 2 * (n_teams - 1));
constraint forall(d in Days) (
    sum(t in Teams) (bool2int(venue[d, t] = BYE)) = 1 /\ sum(t in Teams) (bool2int(venue[d, t] = HOME)) = n_teams div 2 /\ sum(t in Teams) (bool2int(venue[d, t] = AWAY)) = n_teams div 2);

% 1. Mirroring. The dates are grouped into pairs (r1, r2) such that every team
% plays the same opponent on both dates, once at home and once away. The scheme of
% Nemhauser and Trick, (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16),
% (10,17), (11,18), written with dates counted from 0: mirror[d] is the date paired with d
array[Days] of int: mirror = array1d(Days, [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]);
constraint forall(d in Days, t in Teams) (config[d, t] = config[mirror[d], t]);
constraint forall(d in Days, t in Teams) (venue[d, t] = 2 - venue[mirror[d], t]);

% 2. No two final aways. No team can play away on both last dates.
constraint forall(t in Teams)
    (bool2int(venue[n_days - 2, t] = AWAY) + bool2int(venue[n_days - 1, t] = AWAY) <= 1);

% 3. Home/away/bye pattern constraints.
constraint forall(t in Teams) (
    % no team may have more than two home matches in a row
    forall(d in 0..n_days - 3) (sum(k in 0..2) (bool2int(venue[d + k, t] = HOME)) <= 2) /\
    % no team may have more than two away matches in a row
    forall(d in 0..n_days - 3) (sum(k in 0..2) (bool2int(venue[d + k, t] = AWAY)) <= 2) /\
    % no team may have more than three away matches or byes in a row
    forall(d in 0..n_days - 4) (sum(k in 0..3) (bool2int(venue[d + k, t] = AWAY \/ venue[d + k, t] = BYE)) <= 3) /\
    % no team may have more than four home matches or byes in a row
    forall(d in 0..n_days - 5) (sum(k in 0..4) (bool2int(venue[d + k, t] = HOME \/ venue[d + k, t] = BYE)) <= 4));

% 4. Weekend pattern. The second and every later even date (days 1, 3, ...) are
% weekends. Of the weekends, each team plays four at home, four away, and one bye.
array[int] of int: weekends = [d | d in Days where d mod 2 = 1];
constraint forall(t in Teams) (
    sum(d in weekends) (bool2int(venue[d, t] = HOME)) = 4 /\
    sum(d in weekends) (bool2int(venue[d, t] = AWAY)) = 4 /\
    sum(d in weekends) (bool2int(venue[d, t] = BYE)) = 1);

% 5. First weekends. Each team must have home matches or byes at least on two of
% the first five weekends.
constraint forall(t in Teams)
    (sum(i in 1..5) (bool2int(venue[weekends[i], t] = HOME \/ venue[weekends[i], t] = BYE)) >= 2);

% 6. Rival matches. In the last date, every team except FSU plays against its
% rival, unless it plays against FSU or has a bye.
constraint forall(t in Teams where t != FSU)
    (config[n_days - 1, t] = rival[t] \/ config[n_days - 1, t] = FSU \/ venue[n_days - 1, t] = BYE);

% 7. Constrained matches. The pairings Wake-UNC, Wake-Duke, GT-UNC and GT-Duke
% must each occur at least once in dates 11 to 18 (days 10 to 17).
constraint forall(pair in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)])
    (sum(d in 10..n_days - 1) (bool2int(config[d, pair.1] = pair.2)) >= 1);

% 8. Opponent sequence constraints.
% No team (other than UNC and Duke) plays on two consecutive dates away against
% UNC and Duke, in either order.
constraint forall(t in Teams where t != DUKE /\ t != UNC, d in 0..n_days - 2) (
    not (config[d, t] = UNC /\ venue[d, t] = AWAY /\ config[d + 1, t] = DUKE /\ venue[d + 1, t] = AWAY) /\
    not (config[d, t] = DUKE /\ venue[d, t] = AWAY /\ config[d + 1, t] = UNC /\ venue[d + 1, t] = AWAY));
% No team (other than UNC, Duke and Wake) plays on three consecutive dates against
% UNC, Duke and Wake in any order, home or away: the three opponents of those dates
% would then include all three of them.
constraint forall(t in Teams where t != UNC /\ t != DUKE /\ t != WAKE, d in 0..n_days - 3)
    (not (forall(x in [UNC, DUKE, WAKE]) (exists(k in 0..2) (config[d + k, t] = x))));

% 9. Other constraints.
% UNC plays its rival Duke in the last date, and in date 11
constraint config[10, UNC] = DUKE /\ config[n_days - 1, UNC] = DUKE;
% UNC plays Clem in the second date
constraint config[1, UNC] = CLEM;
% Duke has a bye in date 16
constraint venue[15, DUKE] = BYE;
% Wake does not play home in date 17
constraint venue[16, WAKE] != HOME;
% Wake has a bye in the first date
constraint venue[0, WAKE] = BYE;
% Clem, Duke, UMD and Wake do not play away in the last date
constraint forall(t in [CLEM, DUKE, UMD, WAKE]) (venue[n_days - 1, t] != AWAY);
% Clem, FSU, GT and Wake do not play away in the first date
constraint forall(t in [CLEM, FSU, GT, WAKE]) (venue[0, t] != AWAY);
% Neither FSU nor NCSt have a bye in the last date
constraint forall(t in [FSU, NCSt]) (venue[n_days - 1, t] != BYE);
% UNC does not have a bye in the first date
constraint venue[0, UNC] != BYE;

solve satisfy;

output ["{\"config\": [", join(", ", ["[" ++ join(", ", [show(config[d, t]) | t in Teams]) ++ "]" | d in Days]),
        "], \"where\": [", join(", ", ["[" ++ join(", ", [show(venue[d, t]) | t in Teams]) ++ "]" | d in Days]), "]}"];
