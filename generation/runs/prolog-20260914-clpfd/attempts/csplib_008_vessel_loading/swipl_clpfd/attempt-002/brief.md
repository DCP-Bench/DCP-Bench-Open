# csplib_008_vessel_loading

Place n rectangular containers on a deck without overlap, honouring the minimum
separation between classes.

- Instance inputs: `deck_width`, `deck_length`, `n_containers`, `width`,
  `length`, `classes`, `separation`.
- Outputs: `left`, `right` in 0..deck_width and `top`, `bottom` in
  0..deck_length, one per container.
- Satisfaction. Either orientation per container, and for each pair one of the
  four separation inequalities holds.
