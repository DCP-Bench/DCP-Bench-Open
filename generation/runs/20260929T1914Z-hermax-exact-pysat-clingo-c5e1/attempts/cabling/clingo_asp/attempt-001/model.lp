% Cabling: put devices one above another in a rack (one device per slot) so
% that the total cable length is as small as possible. A cable joining two
% devices, or several identical cables between them, costs the distance between
% their slots times the number of cables.
% devices(I, "Name"): device I; cable_struct(K, 0, "A"), cable_struct(K, 1, "B") and
% cable_struct(K, 2, C): cable group K joins A and B with C cables.
device(I) :- devices(I,_).
slot(0..N-1) :- n(N).

% x(I, P): device I is in slot P; every device gets its own slot.
1 { x(I,P) : slot(P) } 1 :- device(I).
:- x(I1,P), x(I2,P), I1 < I2.

% cable(K, I1, I2, C): cable group K joins the devices numbered I1 and I2 with C cables.
cable(K,I1,I2,C) :- cable_struct(K,0,A), cable_struct(K,1,B), cable_struct(K,2,C),
                    devices(I1,A), devices(I2,B).

% The distance between the slots of the two devices of a cable group.
distance(K,|P1 - P2|) :- cable(K,I1,I2,_), x(I1,P1), x(I2,P2).

% The total cable length is what is minimised.
final_sum(S) :- S = #sum { C * D,K : cable(K,_,_,C), distance(K,D) }.
#minimize { S : final_sum(S) }.

#show final_sum/1.
