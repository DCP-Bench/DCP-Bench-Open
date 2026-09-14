include "globals.mzn";

int: deck_width;
int: deck_length;
int: n_containers;
array[int] of int: width;
array[int] of int: length;
array[int] of int: classes;
array[int, int] of int: separation;

array[1..n_containers] of var 0..deck_width: left;
array[1..n_containers] of var 0..deck_width: right;
array[1..n_containers] of var 0..deck_length: top;
array[1..n_containers] of var 0..deck_length: bottom;

array[1..n_containers] of var int: horizontal = [right[i] - left[i] | i in 1..n_containers];
array[1..n_containers] of var int: vertical = [top[i] - bottom[i] | i in 1..n_containers];

% Either orientation of the container.
constraint forall(i in 1..n_containers) (
     (horizontal[i] = width[i] /\ vertical[i] = length[i])
  \/ (horizontal[i] = length[i] /\ vertical[i] = width[i])
);

% Containers keep the separation their classes require.
constraint forall(x, y in 1..n_containers where x < y) (
  let { int: sep = separation[classes[x], classes[y]] } in
     right[x] + sep <= left[y]
  \/ left[x] >= right[y] + sep
  \/ top[x] + sep <= bottom[y]
  \/ bottom[x] >= top[y] + sep
);

% Implied by the constraints above when no separation is negative.
constraint
  if forall(i, j in index_set_1of2(separation)) (separation[i, j] >= 0)
  then diffn(left, bottom, horizontal, vertical)
    /\ cumulative(left, horizontal, vertical, deck_length)
    /\ cumulative(bottom, vertical, horizontal, deck_width)
  else true
  endif;

solve satisfy;

output ["{\"left\": [", join(", ", [show(left[i]) | i in 1..n_containers]),
        "], \"right\": [", join(", ", [show(right[i]) | i in 1..n_containers]),
        "], \"top\": [", join(", ", [show(top[i]) | i in 1..n_containers]),
        "], \"bottom\": [", join(", ", [show(bottom[i]) | i in 1..n_containers]), "]}"];
