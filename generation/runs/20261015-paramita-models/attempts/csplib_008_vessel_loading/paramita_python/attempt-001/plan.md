Containers are cuboid, laid out in a single layer, all positioned parallel to the sides of the deck; each container may be turned by 90 degrees (its width and length swap) -> one Bool rot[c] per non-square container (0 for squares)
left[c] and bottom[c] one-hot over the positions where the container fits inside the deck (0..deck_width-min(width,length), 0..deck_length-min(width,length)); right = left + width + (length-width)*rot, top = bottom + length + (width-length)*rot (integer expressions)
The containers lie within the deck -> right <= deck_width, top <= deck_length; exactly one position per coordinate
Containers must not overlap -> per pair of containers i<j, one Bool per direction: right_i <= left_j, right_j <= left_i, top_i <= bottom_j, top_j <= bottom_i; at least one holds (Or)
Containers of separated classes must be separated by a minimum distance along the deck or across the deck -> the same four alternatives with the separation value s[class_i][class_j] (classes are 1-based indices into the separation matrix) added to the gap
objective -> none (satisfaction); outputs left, right, top, bottom as integer expressions
