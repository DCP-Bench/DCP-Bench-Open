# Plan: session2_color_simple

One-hot colour per country: x_i_c = country i has colour c+1, c in 0..5. Six countries and at most six colours.

- "assign a different colour to the following countries" (six countries) -> N = 6 countries, one-hot x_i_c
- "You can use integers starting from 1 to represent the colours" -> colour value = sum((c+1) * x_i_c)
- "each country has exactly one colour" -> sum(x_i) == 1 per country
- "Two neighbouring countries cannot have the same colour" (graph edges, 1-based in instance) -> ~(x_a_c & x_b_c) per edge and colour c
- "minimizes the number of colours used" -> objective sum over colours c of Or(x_i_c for all i) (colour c is used); no free auxiliary Bools in the objective (see lessons.md)
- "Print the colour assigned to each country as a list (colors) of 6 integers" -> output colors = [sum((c+1) * x_i_c) for each country]
