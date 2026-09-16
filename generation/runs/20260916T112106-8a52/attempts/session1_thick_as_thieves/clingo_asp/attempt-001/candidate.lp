% Thick as thieves: six suspects, at most two guilty, and the innocent tell the
% truth while the guilty lie. Each suspect is guilty exactly when their own
% statement is false.
guilt(0..1).

1 { artie(G) : guilt(G) } 1.
1 { bill(G) : guilt(G) } 1.
1 { crackitt(G) : guilt(G) } 1.
1 { dodgy(G) : guilt(G) } 1.
1 { edgy(G) : guilt(G) } 1.
1 { fingers(G) : guilt(G) } 1.

suspect(artie,G) :- artie(G).
suspect(bill,G) :- bill(G).
suspect(crackitt,G) :- crackitt(G).
suspect(dodgy,G) :- dodgy(G).
suspect(edgy,G) :- edgy(G).
suspect(fingers,G) :- fingers(G).

guilty_count(K) :- K = #count { S : suspect(S,1) }.
% The getaway car barely held two.
:- guilty_count(K), K > 2.

% Bill: "Crackitt did it." Bill lies exactly when Crackitt is innocent.
:- bill(1), crackitt(1).
:- bill(0), crackitt(0).
% Dodgy: "If Crackitt did it, Bill did too." That fails only when Crackitt is
% guilty and Bill is not.
:- dodgy(1), not fails.
:- dodgy(0), fails.
fails :- crackitt(1), bill(0).
% Edgy: "Nobody did it alone." Edgy lies exactly when exactly one is guilty.
:- edgy(1), guilty_count(K), K != 1.
:- edgy(0), guilty_count(1).
% Fingers: "It was Artie and Dodgy together."
both :- artie(1), dodgy(1).
:- fingers(1), both.
:- fingers(0), not both.

#show artie/1.
#show bill/1.
#show crackitt/1.
#show dodgy/1.
#show edgy/1.
#show fingers/1.
