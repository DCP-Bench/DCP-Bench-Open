% Problem: eighteen_hole_golf
% Generate a random 18-hole golf course where each hole has a length of 3, 4, or 5,
% and the total length of the course is 72. Output: the lengths of the holes
% (holes) as a list of 18 integers.

:- lib(ic).

model(_Instance, Vars, [holes-Holes], none) :-
    length(Holes, 18),
    Holes :: 3..5,

    % each hole has a length of 3, 4, or 5
    % and the total length of the course is 72.
    sum(Holes) #= 72,

    Vars = Holes.
