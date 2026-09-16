% Four islands: name, export and attraction for each of four islands laid out
% as A B over C D, with bridges A-B, C-D, A-C and B-D. Every value is a map
% position: A=0, B=1, C=2, D=3.
spot(0..3).
idx(0..3).

1 { island(I,S) : spot(S) } 1 :- idx(I).
1 { export(I,S) : spot(S) } 1 :- idx(I).
1 { attraction(I,S) : spot(S) } 1 :- idx(I).
:- island(I,S), island(J,S), I < J.
:- export(I,S), export(J,S), I < J.
:- attraction(I,S), attraction(J,S), I < J.

% island: Pwana Quero Rayou Skern ; export: alabaster bananas coconuts durian
% attraction: hotel ice_rink jai_alai koala
% 1. The koala preserve is due south of Pwana.
:- island(0,P), attraction(3,K), not southof(P,K).
southof(0,2).
southof(1,3).
% 2. The alabaster quarry is due west of Quero.
:- export(0,A), island(1,Q), not westof(A,Q).
westof(0,1).
westof(2,3).
% 3. The resort hotel is due east of the durian fruit exporter.
:- export(3,D), attraction(0,H), not westof(D,H).
% 4. Skern and the jai alai stadium share a north-south bridge.
:- island(3,S), attraction(2,J), not northsouth(S,J).
northsouth(0,2). northsouth(2,0). northsouth(1,3). northsouth(3,1).
% 5. Rayou and the banana exporter share an east-west bridge.
:- island(2,R), export(1,B), not eastwest(R,B).
eastwest(0,1). eastwest(1,0). eastwest(2,3). eastwest(3,2).
% 6. The ice rink and the jai alai stadium have no bridge between them.
:- attraction(1,I), attraction(2,J), not diagonal(I,J).
diagonal(0,3). diagonal(3,0). diagonal(1,2). diagonal(2,1).

#show island/2.
#show export/2.
#show attraction/2.
