% Arch friends: the order in which Harriet bought four pairs of shoes and where
% she bought each. Every value is a stop number from 1 to 4.
stop(1..4).

1 { ecruespadrilles(S) : stop(S) } 1.
1 { fuchsiaflats(S) : stop(S) } 1.
1 { purplepumps(S) : stop(S) } 1.
1 { suedesandals(S) : stop(S) } 1.
shoe(ecru,S) :- ecruespadrilles(S).
shoe(fuchsia,S) :- fuchsiaflats(S).
shoe(purple,S) :- purplepumps(S).
shoe(suede,S) :- suedesandals(S).
:- shoe(X,S), shoe(Y,S), X < Y.

1 { footfarm(S) : stop(S) } 1.
1 { heelsinahandcart(S) : stop(S) } 1.
1 { theshoepalace(S) : stop(S) } 1.
1 { tootsies(S) : stop(S) } 1.
store(farm,S) :- footfarm(S).
store(heels,S) :- heelsinahandcart(S).
store(palace,S) :- theshoepalace(S).
store(toots,S) :- tootsies(S).
:- store(X,S), store(Y,S), X < Y.

% 1. Fuchsia flats came from Heels in a Handcart.
:- fuchsiaflats(S), heelsinahandcart(T), S != T.
% 2. The stop after the purple pumps was not Tootsies.
:- purplepumps(S), tootsies(T), T == S + 1.
% 3. The Foot Farm was the second stop.
:- not footfarm(2).
% 4. The suede sandals came two stops after The Shoe Palace.
:- theshoepalace(S), suedesandals(T), T != S + 2.

#show ecruespadrilles/1.
#show fuchsiaflats/1.
#show purplepumps/1.
#show suedesandals/1.
#show footfarm/1.
#show heelsinahandcart/1.
#show theshoepalace/1.
#show tootsies/1.
