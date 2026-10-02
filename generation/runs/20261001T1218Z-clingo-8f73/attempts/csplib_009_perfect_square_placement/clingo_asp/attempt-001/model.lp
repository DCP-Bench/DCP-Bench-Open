% Perfect square placement: pack squares of given integer sizes into a larger square so that
% no two squares overlap and all borders are parallel to the border of the large square. The
% areas of the small squares add up to the area of the large one, so nothing is left over.
% Instance facts: base(B): the side of the large square; sides(I, S): small square I has side S.
% Coordinates are the lower-left corner of a square, counted from 0.
square(I) :- sides(I,_).

% x_coords(I, X) and y_coords(I, Y): the position of square I. A square must lie inside the
% large square, so its lower-left corner is at most base - side.
1 { x_coords(I,X) : X = 0..B - S } 1 :- sides(I,S), base(B).
1 { y_coords(I,Y) : Y = 0..B - S } 1 :- sides(I,S), base(B).

% The columns and rows that square I spans, and so the unit cells it covers. Spans are derived
% for x and y separately and combined afterwards: deriving the cells from the corner directly
% would instantiate (positions x positions x cells) rules, far too many for a large base.
x_span(I,C) :- x_coords(I,X), sides(I,S), C = X..X + S - 1.
y_span(I,C) :- y_coords(I,Y), sides(I,S), C = Y..Y + S - 1.
covers(I,CX,CY) :- x_span(I,CX), y_span(I,CY).

% No overlap between squares: a unit cell belongs to at most one square.
:- base(B), CX = 0..B - 1, CY = 0..B - 1, #count { I : covers(I,CX,CY) } > 1.

% The squares fill the large square exactly (their areas add up to its area, which the
% problem requires), so every unit cell is covered. This is implied by the two groups
% above; stating it lets the solver learn from empty cells early.
:- base(B), CX = 0..B - 1, CY = 0..B - 1, not covers(_,CX,CY).

#show x_coords/2.
#show y_coords/2.
