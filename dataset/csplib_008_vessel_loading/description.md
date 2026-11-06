Supply vessels transport containers from site to site. The deck area is rectangular. Containers are cuboid, and are
laid out in a single layer. All containers are positioned parallel to the sides of the deck. The contents of the
containers determine their class. Certain classes of containers are constrained to be separated by minimum distances
either along the deck or across the deck.

A container occupies the area from `left` to `right` across the width of the deck, and from `bottom` to `top` along its
length, with `right - left` and `top - bottom` being its width and length, in that order or rotated by 90 degrees. All
of these lie between 0 and the deck's size in that direction. Two containers may touch. `separation[a-1][b-1]` is the
distance that containers of classes `a` and `b` must keep in at least one of the two directions.

The vessel loading decision problem is to determine whether a given set of containers can be positioned on a given
deck, without overlapping, and without violating any of the separation constraints.

Print the positions of the containers (left, right, top, bottom), as lists of integers - starting from 0.
