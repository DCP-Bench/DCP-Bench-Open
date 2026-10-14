Map positions: A=0 (NW), B=1 (NE), C=2 (SW), D=3 (SE). Bridges: A-B, C-D (east-west); A-C, B-D (north-south).
Islands by name: island[k] = map position, k = Pwana 0, Quero 1, Rayou 2, Skern 3.
Export index: alabaster 0, bananas 1, coconuts 2, durian 3. Attraction index: hotel 0, rink 1, jai alai 2, koala 3.

Each island name is a map position, all different -> island distinct(IPL_DOM).
Each island has one export and one attraction -> ex[k], at[k] distinct(IPL_DOM) over 0..3.
Link name to export: island k has export e -> exP[ex[k]] = island[k] -> element(exP, ex[k], island[k]).
Link name to attraction -> element(atP, at[k], island[k]).
Export and attraction positions are permutations -> distinct(exP), distinct(atP).

Relations between two map positions as extensional tables over the 4 positions (2x2 map):
  X due south of Y -> extensional (X,Y) in {(2,0),(3,1)}
  X due east of Y -> extensional (X,Y) in {(1,0),(3,2)}
  X due west of Y -> extensional (X,Y) in {(0,1),(2,3)} (used for alabaster west of Quero)
  X north-south bridge to Y -> extensional (X,Y) in {(0,2),(2,0),(1,3),(3,1)}
  X east-west bridge to Y -> extensional (X,Y) in {(0,1),(1,0),(2,3),(3,2)}
Clue 1 koala (atP[3]) due south of Pwana (island[0]) -> south table (atP[3], island[0]).
Clue 2 alabaster (exP[0]) due west of Quero (island[1]) -> west table (exP[0], island[1]).
Clue 3 resort hotel (atP[0]) due east of durian (exP[3]) -> east table (atP[0], exP[3]).
Clue 4 Skern (island[3]) and jai alai (atP[2]) north-south bridge -> NS table.
Clue 5 Rayou (island[2]) and bananas (exP[1]) east-west bridge -> EW table.
Clue 6 rink (atP[1]) and jai alai (atP[2]) not bridged -> forbidden-tuple form of the adjacency table (both bridge kinds), extensional(..., false).
Branching: island, ex, at with INT_VAR_SIZE_MIN and INT_VAL_MIN; no objective (satisfaction).
Instance has no fields; constructor ignores the instance argument, all data is from the problem statement.
