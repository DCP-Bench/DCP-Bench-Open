% Movie scheduling: from the offered movie projects, accept as many as possible such that no two
% accepted ones have overlapping filming periods (first and last day both count as filming days).
% Instance facts: movies(I,0,Title), movies(I,1,FirstDay), movies(I,2,LastDay) for movie I.
% The title is a string and is never needed.
movie(I) :- movies(I,0,_).

% selected(I): movie I is accepted.
{ selected(I) } :- movie(I).

% Two different movies whose filming periods overlap (each ends on or after the day the other
% starts) cannot both be accepted.
:- selected(I), selected(J), I < J,
   movies(I,1,StartI), movies(I,2,EndI), movies(J,1,StartJ), movies(J,2,EndJ),
   EndI >= StartJ, EndJ >= StartI.

% Maximise the number of accepted movies.
#maximize { 1,I : selected(I) }.

% selected_movies(I, true/false): whether movie I is accepted.
selected_movies(I,true)  :- selected(I).
selected_movies(I,false) :- movie(I), not selected(I).

#show selected_movies/2.
