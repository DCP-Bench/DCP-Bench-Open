idx(0..M-1) :- m(M).

% One value per cell.
1 { quasigroup(I,J,V) : idx(V) } 1 :- idx(I), idx(J).

% Every value occurs once in each row and once in each column.
:- idx(I), idx(V), #count { J : quasigroup(I,J,V) } != 1.
:- idx(J), idx(V), #count { I : quasigroup(I,J,V) } != 1.

% QG3: (a*b)*(b*a) = a. ASP indexes by the decision values directly, so this
% needs no auxiliary array.
:- idx(A), idx(B), quasigroup(A,B,X), quasigroup(B,A,Y), quasigroup(X,Y,Z), Z != A.

#show quasigroup/3.
