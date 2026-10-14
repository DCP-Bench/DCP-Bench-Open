% Who killed Aunt Agatha? Agatha, the butler and Charles are the only people in Dreadsbury
% Mansion. A killer always hates, and is no richer than, his victim. Charles hates no one that
% Agatha hates. Agatha hates everybody except the butler. The butler hates everyone not richer
% than Agatha, and everyone whom Agatha hates. No one hates everyone.
% Instance: names(I, Name) lists the people, numbered from 0; the output is the killer's number.

% The three people of the story, as numbers in the order of the instance's name list. This
% order is part of the problem statement, and the instance only supplies the names.
#const agatha = 0.
#const butler = 1.
#const charles = 2.
person(0..N-1) :- N = #count { I : names(I,_) }.
people(N) :- N = #count { I : names(I,_) }.

% Agatha is the victim; the killer is one of the people.
1 { killer(K) : person(K) } 1.

% hates(X,Y): X hates Y. richer(X,Y): X is richer than Y.
{ hates(X,Y) : person(X), person(Y) }.
{ richer(X,Y) : person(X), person(Y) }.

% A killer always hates his victim and is no richer than the victim.
:- killer(K), not hates(K,agatha).
:- killer(K), richer(K,agatha).

% Richness: nobody is richer than himself, and of two different people exactly one is richer.
:- richer(X,X).
:- person(X), person(Y), X < Y, richer(X,Y), richer(Y,X).
:- person(X), person(Y), X < Y, not richer(X,Y), not richer(Y,X).

% Charles hates no one that Agatha hates.
:- hates(agatha,X), hates(charles,X).

% Agatha hates everybody except the butler.
:- person(X), X != butler, not hates(agatha,X).
:- hates(agatha,butler).

% The butler hates everyone not richer than Agatha.
:- person(X), not richer(X,agatha), not hates(butler,X).

% The butler hates everyone whom Agatha hates.
:- hates(agatha,X), not hates(butler,X).

% No one hates everyone.
:- person(X), people(N), #count { Y : hates(X,Y) } >= N.

#show killer/1.
