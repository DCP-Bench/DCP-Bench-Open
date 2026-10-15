# four_islands plan
Map positions: A=0 (NW), B=1 (NE), C=2 (SW), D=3 (SE). Each island has one position; the island at a position has one export and one attraction.
- Four islands (Pwana, Quero, Rayou, Skern) each on a different position -> one-hot isl[k][p], exactly one per island, one per position.
- Four exports each on a different position -> one-hot exp[j][p].
- Four attractions each on a different position -> one-hot att[j][p].
- Clue 1 "koala preserve island is due south of Pwana" -> pos(koala) = pos(Pwana) + 2 (same column, lower row); for all p,q: Pwana at p and koala at q require q due south of p.
- Clue 2 "largest alabaster quarry is due west of Quero" -> alabaster at p, Quero at q requires same row, col(p) < col(q).
- Clue 3 "resort hotel is due east of durian" -> hotel at p, durian at q requires same row, col(p) > col(q).
- Clue 4 "Skern and jai alai stadium connected by north-south bridge" -> same column, different row.
- Clue 5 "Rayou and bananas connected by east-west bridge" -> same row, different column.
- Clue 6 "ice skating rink and jai alai not connected by bridge" -> different row and different column (diagonal).
- Output island[k] = sum(p * isl[k][p]), export[j], attraction[j] likewise.
- Objective: satisfaction.
