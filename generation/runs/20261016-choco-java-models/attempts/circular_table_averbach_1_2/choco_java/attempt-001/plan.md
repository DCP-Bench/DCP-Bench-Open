# circular_table_averbach_1_2 plan (attempt-001)

Seats 0, 1, 2 around the table; seat p's right neighbour is (p+1) mod 3 (1 is right of 0, 2 right of 1, 0 right of 2).
Players X, Y, Z occupy seats x, y, z (all different). Nationalities american, english, french are seats (all different).
- "X, Y, Z are seated around the table, each a different person" -> allDifferent(x, y, z)
- "American, English, French are the three nationalities" -> allDifferent(american, english, french)
- "Y passed three hearts to the American" -> right(Y) is the American: table (y, american) = {(0,1),(1,2),(2,0)}
- "X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman" -> the person P who passes to French is on French's left; X passes to P, so P = right(X) and french = right(P) = (x+2) mod 3: table (x, french) = {(0,2),(1,0),(2,1)}
- Objective: none (satisfaction). Outputs: x, y, z, american, english, french.
