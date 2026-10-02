% Perfect square placement: pack squares of the given integer sizes into a large
% square, with no overlaps and sides parallel to the large square's sides. The
% areas of the small squares add up to the area of the large one, so nothing is left over.
include "globals.mzn";

int: base;                    % side length of the large square
array[int] of int: sides;     % side lengths of the small squares

set of int: Squares = index_set(sides);

% (x_coords[i], y_coords[i]) = lower-left corner of square i, counted from 0.
% The domain upper bound base - sides[i] makes every square lie inside the large square.
array[Squares] of var int: x_coords;
array[Squares] of var int: y_coords;
constraint forall(i in Squares) (x_coords[i] >= 0 /\ x_coords[i] <= base - sides[i]);
constraint forall(i in Squares) (y_coords[i] >= 0 /\ y_coords[i] <= base - sides[i]);

% no two squares overlap: for every pair one lies to the left of, right of,
% below or above the other (diffn states exactly this for rectangles)
constraint diffn(x_coords, y_coords, sides, sides);

% Implied: no square overlaps another and the areas add up to the area of the
% large square, so every unit-wide vertical strip of the large square is
% covered completely: the squares that cross the strip have sides adding up to
% base. The same holds for every horizontal strip. This follows from the
% constraints above and removes no solution; it gives Gecode much stronger
% propagation than the pairwise non-overlap alone.
constraint forall(c in 0..base - 1)
    (sum(i in Squares) (sides[i] * bool2int(x_coords[i] <= c /\ c < x_coords[i] + sides[i])) = base);
constraint forall(c in 0..base - 1)
    (sum(i in Squares) (sides[i] * bool2int(y_coords[i] <= c /\ c < y_coords[i] + sides[i])) = base);

solve satisfy;

output ["{\"x_coords\": [", join(", ", [show(x_coords[i]) | i in Squares]),
        "], \"y_coords\": [", join(", ", [show(y_coords[i]) | i in Squares]), "]}"];
