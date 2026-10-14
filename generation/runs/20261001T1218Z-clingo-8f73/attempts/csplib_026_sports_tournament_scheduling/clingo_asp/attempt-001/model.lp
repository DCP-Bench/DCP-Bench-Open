% Sports tournament scheduling: n teams play over n-1 weeks, each week has n/2 periods, and each
% period holds one match: the first team in a match plays at home, the second plays away.
% Every team plays once a week, every team plays every other team, and every team plays at most
% twice in the same period over the whole tournament. Teams are numbered from 1 to n.
% Instance facts: n_teams(N).
team(1..N) :- n_teams(N).
week(0..N-2) :- n_teams(N).
period(0..N/2-1) :- n_teams(N).

% home(W,P,T) / away(W,P,T): team T is the home / away team of the match in week W and period P.
1 { home(W,P,T) : team(T) } 1 :- week(W), period(P).
1 { away(W,P,T) : team(T) } 1 :- week(W), period(P).

% A team cannot play itself.
:- home(W,P,T), away(W,P,T).

% Every team plays once a week: the teams of the week's matches are all different, home and away together.
:- week(W), team(T), #count { P,h : home(W,P,T) ; P,a : away(W,P,T) } != 1.

% Every team plays every other team: for each pair, some match has one of them at home and the other away.
played(T1,T2) :- home(W,P,T1), away(W,P,T2), T1 < T2.
played(T1,T2) :- home(W,P,T2), away(W,P,T1), T1 < T2.
:- team(T1), team(T2), T1 < T2, not played(T1,T2).

% Every team plays at most twice in the same period over the tournament.
:- team(T), period(P), #count { W,h : home(W,P,T) ; W,a : away(W,P,T) } > 2.

#show home/3.
#show away/3.
