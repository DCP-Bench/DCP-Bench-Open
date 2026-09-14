vertex(0..N-1) :- n(N).

% Choose the undirected edges, then mirror them into the declared matrix.
{ edge(I,J) } :- vertex(I), vertex(J), I < J.
matrix(I,J,1) :- edge(I,J).
matrix(J,I,1) :- edge(I,J).
matrix(I,J,0) :- vertex(I), vertex(J), not edge(I,J), not edge(J,I).

% Every degree is nonzero and a multiple of three.
degree(I,D) :- vertex(I), D = #count { J : matrix(I,J,1) }.
:- degree(I,0).
:- degree(I,D), D \ 3 != 0.

% The whole matrix holds a multiple of twelve ones.
:- T = #count { I,J : matrix(I,J,1) }, T \ 12 != 0.

% Diamond-free: no four vertices span five or more of their six edges.
:- vertex(A), vertex(B), vertex(C), vertex(D), A < B, B < C, C < D,
   5 #sum { 1,1 : edge(A,B); 1,2 : edge(A,C); 1,3 : edge(A,D);
            1,4 : edge(B,C); 1,5 : edge(B,D); 1,6 : edge(C,D) }.

#show matrix/3.
