% Map colouring: adjacent countries differ in colour, and the highest colour
% number used is as small as possible.

% The instance carries only the edge list, so the country count is the largest
% 1-based country id appearing in it.
endpoint(X) :- graph(_,_,X).
countries(N) :- N = #max { X : endpoint(X) }.
country(1..N) :- countries(N).
% Colours run 1..num_nodes, as in the reference.
colour(1..N) :- countries(N).

1 { colourof(I,C) : colour(C) } 1 :- country(I).

% Two countries joined by an edge differ in colour.
:- graph(E,0,A), graph(E,1,B), colourof(A,C), colourof(B,C).

used(M) :- M = #max { C : colourof(_,C) }.
#minimize { M : used(M) }.

% The declared output is a list, so the 1-based country becomes a 0-based index.
colors(I-1,C) :- colourof(I,C).
#show colors/2.
