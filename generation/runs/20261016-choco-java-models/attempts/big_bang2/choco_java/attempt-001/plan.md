Problem: five nontransitive dice (Rock 0, Paper 1, Scissors 2, Lizard 3, Spock 4), each with six faces in 1..12; A beats B when A has a strictly larger face than B in more than half of the 36 face pairs (more than 18).
Each face value between 1 and 12 inclusive -> dice[d][f] domain 1..12
For each of the ten beats relationships (winner, loser): count of face pairs (a in winner, b in loser) with a > b must be more than half of 36 -> sum of 36 reified (a > b) >= 19
Rock crushes Scissors -> (0,2); Rock crushes Lizard -> (0,3); Paper covers Rock -> (1,0); Paper disproves Spock -> (1,4); Scissors cuts Paper -> (2,1); Scissors decapitate Lizard -> (2,3); Lizard eats Paper -> (3,1); Lizard poisons Spock -> (3,4); Spock vaporizes Rock -> (4,0); Spock smashes Scissors -> (4,2)
Objective: satisfaction (none)
Symmetry (not in the statement): faces of a die are a multiset, so increasing(dice[d]) keeps all beats relations -> m.increasing(dice[d], 0)
Search: domOverWDeg over all faces with Luby restarts (added after quick check hit execution_timeout on the second solution with default search)
