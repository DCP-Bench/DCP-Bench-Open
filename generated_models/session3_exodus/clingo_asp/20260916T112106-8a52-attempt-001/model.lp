% Exodus: match five children to an age, a country of origin and a part of the
% story. Every value is a group number 1..5, and two values sharing a number
% describe the same child.
group(1..5).
idx(0..4).

1 { ages(I,G) : group(G) } 1 :- idx(I).
1 { children(I,G) : group(G) } 1 :- idx(I).
1 { countries(I,G) : group(G) } 1 :- idx(I).
1 { stories(I,G) : group(G) } 1 :- idx(I).
:- ages(I,G), ages(J,G), I < J.
:- children(I,G), children(J,G), I < J.
:- countries(I,G), countries(J,G), I < J.
:- stories(I,G), stories(J,G), I < J.

% The age slots stand for these actual ages, in order.
years(0,3). years(1,5). years(2,7). years(3,8). years(4,10).

% 1. Debby (children 2) is from Lithuania (countries 2).
:- children(2,G), countries(2,H), G != H.
% 2. The Passover child (stories 3) is two years older than Bernice (children 0).
:- ages(I,G), stories(3,G), ages(J,H), children(0,H),
   years(I,X), years(J,Y), X != Y + 2.
% 3. The Yemeni child (countries 4) is younger than the Ethiopian (countries 0).
:- ages(I,G), countries(4,G), ages(J,H), countries(0,H),
   years(I,X), years(J,Y), X >= Y.
% 4. The Moroccan child (countries 3) is three years older than Ted (children 4).
:- ages(I,G), countries(3,G), ages(J,H), children(4,H),
   years(I,X), years(J,Y), X != Y + 3.
% 5. Sammy (children 3) is three years older than the Moses child (stories 2).
:- ages(I,G), children(3,G), ages(J,H), stories(2,H),
   years(I,X), years(J,Y), X != Y + 3.

#show ages/2.
#show children/2.
#show countries/2.
#show stories/2.
