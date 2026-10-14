% Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors
% of a five-floor house; the clues rule out some floors and some neighbours.
% The puzzle is fixed by the problem; the instance carries no data.
% floor(P, V): person P lives on floor V; b, c, f, m and s are the initials of
% Baker, Cooper, Fletcher, Miller and Smith.
person(b;c;f;m;s).
1 { floor(P,V) : V = 1..5 } 1 :- person(P).

% They all live on different floors.
:- floor(P,V), floor(Q,V), P < Q.

% Baker does not live on the fifth floor.
:- floor(b,5).
% Cooper does not live on the first floor.
:- floor(c,1).
% Fletcher lives neither on the fifth nor on the first floor.
:- floor(f,5).
:- floor(f,1).
% Miller lives on a higher floor than Cooper.
:- floor(m,VM), floor(c,VC), VM <= VC.
% Smith does not live on a floor adjacent to Fletcher's.
:- floor(s,VS), floor(f,VF), |VS-VF| = 1.
% Fletcher does not live on a floor adjacent to Cooper's.
:- floor(f,VF), floor(c,VC), |VF-VC| = 1.

% The answer: one atom per person, b(V), c(V), ...
b(V) :- floor(b,V).
c(V) :- floor(c,V).
f(V) :- floor(f,V).
m(V) :- floor(m,V).
s(V) :- floor(s,V).
#show b/1.
#show c/1.
#show f/1.
#show m/1.
#show s/1.
