% Perfect square placement: pack squares of given integer sizes into a larger square so that
% no two squares overlap and all borders are parallel to the border of the large square. The
% areas of the small squares add up to the area of the large one, so nothing is left over.
% Instance facts: base(B): the side of the large square; sides(I, S): small square I has side S.
% Coordinates are the lower-left corner of a square, counted from 0.
square(I) :- sides(I,S).

% Each coordinate is written as thresholds: xge(I, V) says the x coordinate of square I is at
% least V, yge(I, V) the same for y. A square must lie inside the large square, so its
% coordinates run from 0 to base - side. Thresholds are nested (at least V + 1 implies at least V).
% Thresholds make "square J lies to the right of square I" a set of short implications, which
% the solver propagates well; naming every pair of coordinates would grow with the base squared.
{ xge(I,V) } :- sides(I,S), base(B), V = 1..B - S.
{ yge(I,V) } :- sides(I,S), base(B), V = 1..B - S.
:- xge(I,V), V > 1, not xge(I,V - 1).
:- yge(I,V), V > 1, not yge(I,V - 1).

% x_coords(I, X) and y_coords(I, Y): the position of square I, the largest threshold it reaches.
x_coords(I,X) :- xge(I,X), not xge(I,X + 1).
x_coords(I,0) :- square(I), not xge(I,1).
y_coords(I,Y) :- yge(I,Y), not yge(I,Y + 1).
y_coords(I,0) :- square(I), not yge(I,1).

% bad_x(I, J): it is not the case that square I lies entirely to the left of square J, that is
% x_I + side_I <= x_J fails: square J starts too early for some threshold V reached by square I
% (V = 0 included, which every square reaches). bad_y is the same vertically.
bad_x(I,J) :- square(I), square(J), I != J, sides(I,SI), not xge(J,SI).
bad_x(I,J) :- xge(I,V), square(J), I != J, sides(I,SI), not xge(J,V + SI).
bad_y(I,J) :- square(I), square(J), I != J, sides(I,SI), not yge(J,SI).
bad_y(I,J) :- yge(I,V), square(J), I != J, sides(I,SI), not yge(J,V + SI).

% No overlap between squares: of any two squares, one lies left of the other or below it.
:- square(I), square(J), I < J, bad_x(I,J), bad_x(J,I), bad_y(I,J), bad_y(J,I).

% The columns and rows that square I spans.
x_span(I,C) :- x_coords(I,X), sides(I,S), C = X..X + S - 1.
y_span(I,C) :- y_coords(I,Y), sides(I,S), C = Y..Y + S - 1.

% The squares fill the large square exactly (their areas add up to its area, which the
% problem requires), so the squares that cross any column, and likewise any row, have sides that
% add up to the base. This is implied by the no-overlap and the area, and is stated so the
% solver can use it to prune early.
:- base(B), C = 0..B - 1, B != #sum { S,I : x_span(I,C), sides(I,S) }.
:- base(B), C = 0..B - 1, B != #sum { S,I : y_span(I,C), sides(I,S) }.

#show x_coords/2.
#show y_coords/2.
