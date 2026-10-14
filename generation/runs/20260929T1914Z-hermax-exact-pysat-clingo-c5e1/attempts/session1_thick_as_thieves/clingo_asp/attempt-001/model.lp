% Thick as thieves: six suspects, at most two of them guilty. The innocent tell
% the truth and the guilty lie in what they said.
% The puzzle is fixed by the problem; the instance carries no data.
suspect(artie;bill;crackitt;dodgy;edgy;fingers).
{ guilty(S) } :- suspect(S).

% The getaway car held two, so at most two are guilty.
:- #count { S : guilty(S) } > 2.

% A suspect is guilty exactly when what he said is false.
% Artie: "It wasn't me." and Crackitt: "No I wasn't." Each is guilty exactly when he
% says something false about himself, which holds for either value, so neither
% statement restricts anything.
% Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
:- guilty(bill), guilty(crackitt).
:- not guilty(bill), not guilty(crackitt).
% Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt is
% guilty and Bill is not, and then Dodgy is guilty.
:- guilty(dodgy), not guilty(crackitt).
:- guilty(dodgy), guilty(bill).
:- not guilty(dodgy), guilty(crackitt), not guilty(bill).
% Edgy: "Nobody did it alone." False exactly when at most one suspect is guilty.
:- guilty(edgy), #count { S : guilty(S) } > 1.
:- not guilty(edgy), #count { S : guilty(S) } <= 1.
% Fingers: "That's right: it was Artie and Dodgy together." False exactly when Artie
% and Dodgy are not both guilty.
:- guilty(fingers), guilty(artie), guilty(dodgy).
:- not guilty(fingers), not guilty(artie).
:- not guilty(fingers), not guilty(dodgy).

% The answer: one atom per suspect, 1 when guilty and 0 otherwise.
artie(1) :- guilty(artie).
artie(0) :- not guilty(artie).
bill(1) :- guilty(bill).
bill(0) :- not guilty(bill).
crackitt(1) :- guilty(crackitt).
crackitt(0) :- not guilty(crackitt).
dodgy(1) :- guilty(dodgy).
dodgy(0) :- not guilty(dodgy).
edgy(1) :- guilty(edgy).
edgy(0) :- not guilty(edgy).
fingers(1) :- guilty(fingers).
fingers(0) :- not guilty(fingers).
#show artie/1.
#show bill/1.
#show crackitt/1.
#show dodgy/1.
#show edgy/1.
#show fingers/1.
