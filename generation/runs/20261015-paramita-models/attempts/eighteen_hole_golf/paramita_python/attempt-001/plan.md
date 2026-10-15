Generate a random 18-hole golf course -> 18 holes, one-hot Bools per hole over lengths {3,4,5}, holes[i] = sum(v * h[i][v])
each hole has a length of 3, 4, or 5 -> sum(h[i][v] for v in 3,4,5) == 1 per hole
the total length of the course is 72 -> sum over all holes and lengths of v * h[i][v] == 72
Print the lengths of the holes as a list of 18 integers -> outputs {"holes": holes}, holes as integer expressions
objective: satisfaction (no objective)
