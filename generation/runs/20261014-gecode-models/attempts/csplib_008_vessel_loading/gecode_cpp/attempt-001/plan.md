# Plan: vessel loading (attempt 001)

Containers are placed in a deck_width x deck_length rectangle as axis-parallel rectangles, each optionally turned by 90 degrees (rot[i]). Edges are exclusive: right = left + effective width, top = bottom + effective length.

- each container lies inside the deck: left, right in 0..deck_width; bottom, top in 0..deck_length -> IntVar domains
- rot[i] in 0..1; effective x extent w[i] = width if rot 0, length if rot 1 -> element(IntArgs({width, length}), rot, w)
- effective y extent h[i] = length if rot 0, width if rot 1 -> element(IntArgs({length, width}), rot, h)
- right = left + w; top = bottom + h -> rel (linear equality)
- containers do not overlap -> nooverlap(left, w, right, bottom, h, top) (variable-size rectangles with end points)
- containers of classes with separation s > 0 are at least s apart along the deck or across it: per pair, four reified gaps (left_j >= right_i + s, and the three others) -> clause BOT_OR over the four BoolVars (s = 0 is covered by non-overlap)
- cell view: inX/inY reify column and row spans per container; owner[c] in 0..n per cell, channel(cover, owner, 0) makes each cell covered by at most one container (redundant; propagates on tight decks, no decomposition of the globals)
- total container area equal to deck area -> every cell owned (rel owner != 0); data-derived implied constraint, posted only then
- branching: owner (INT_VAR_NONE, INT_VAL_MAX so the empty cell is tried last), then rot, then left and bottom (INT_VAR_SIZE_MIN, INT_VAL_MIN)
- objective: none (satisfaction); outputs left, right, bottom, top
