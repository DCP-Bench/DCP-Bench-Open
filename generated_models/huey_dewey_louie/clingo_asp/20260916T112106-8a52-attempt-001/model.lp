% Huey, Dewey and Louie: three cub scouts who cannot lie, so each of their
% statements is simply true.
guilt(0..1).

1 { huey(G) : guilt(G) } 1.
1 { dewey(G) : guilt(G) } 1.
1 { louie(G) : guilt(G) } 1.

% Huey: Dewey and Louie share equally.
:- dewey(A), louie(B), A != B.
% Dewey: if Huey is guilty, so am I.
:- huey(1), dewey(0).
% Louie: Dewey and I are not both guilty.
:- dewey(1), louie(1).

#show huey/1.
#show dewey/1.
#show louie/1.
