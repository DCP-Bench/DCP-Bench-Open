Five dice, each with six faces valued 1..12, in a 5x6 array dice[die][face]. Rows: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.
Face values may repeat within and across dice; no symmetry breaking (faces are unordered in the description, so none is imposed).
Each die has six faces with values in 1..12 -> IntVarArray x(*this, 30, 1, 12) viewed as Matrix<IntVarArray> dice(x, 6, 5) (6 columns = faces, 5 rows = dice).
Rock(1) crushes Scissors(3): A beats B when A has a strictly larger face in more than half of the 36 face pairs -> 36 BoolVars b = expr(*this, dice(f,A) > dice(g,B)), then linear(*this, bools, IRT_GQ, 19) (more than 18 of 36). Decomposition: no global counts pairs of faces; the reified sum is the only row that fits.
Rock(1) crushes Lizard(4): same pattern for dice pair (0,3).
Paper(2) covers Rock(1): same pattern for dice pair (1,0).
Paper(2) disproves Spock(5): same pattern for dice pair (1,4).
Scissors(3) cuts Paper(2): same pattern for dice pair (2,1).
Scissors(3) decapitate Lizard(4): same pattern for dice pair (2,3).
Lizard(4) eats Paper(2): same pattern for dice pair (3,1).
Lizard(4) poisons Spock(5): same pattern for dice pair (3,4).
Spock(5) vaporizes Rock(1): same pattern for dice pair (4,0).
Spock(5) smashes Scissors(3): same pattern for dice pair (4,2).
Branching: branch on all 30 face values, INT_VAR_SIZE_MIN, INT_VAL_MIN (satisfaction; search is small).
Objective: satisfaction, no objective.
