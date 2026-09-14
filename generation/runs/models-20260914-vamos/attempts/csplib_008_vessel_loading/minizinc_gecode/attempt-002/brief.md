# csplib_008_vessel_loading

Place n rectangular containers on a rectangular deck without overlap, honouring
the minimum separation required between their classes.

- Instance inputs: `deck_width`, `deck_length`, `n_containers`, `width`,
  `length`, `classes` (1-based class of each container), `separation`
  (class-by-class separation matrix).
- Outputs: `left`, `right` (integers in 0..deck_width) and `top`, `bottom`
  (integers in 0..deck_length), one per container.
- Satisfaction. Each container takes either orientation:
  right-left = width and top-bottom = length, or the two swapped. For each pair
  x < y with sep = separation[classes[x]-1][classes[y]-1], one of
  right[x] + sep <= left[y], left[x] >= right[y] + sep,
  top[x] + sep <= bottom[y], bottom[x] >= top[y] + sep holds.
