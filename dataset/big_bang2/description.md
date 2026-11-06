Nontransitive dice: The idea is to create a set of five dice such that the dominance relationships
between the dice is isomorphic to the corresponding relationships in the game
Rock-Paper-Scissors extended by the choices Lizard and Spock.
Each choice beats two other choices and is beaten by two other choices.
In particular, we have the following ten 'beats' relationships

1:  Rock(1) crushes Scissors(3)
2:  Rock(1) crushes Lizard(4)
3:  Paper(2) covers Rock(1)
4:  Paper(2) disproves Spock(5)
5:  Scissors(3) cuts Paper(2)
6:  Scissors(3) decapitate Lizard(4)
7:  Lizard(4) eats Paper(2)
8:  Lizard(4) poisons Spock(5)
9:  Spock(5) vaporizes Rock(1)
10: Spock(5) smashes Scissors(3)

Each die has six integer-valued faces, and each face value must be between 1 and 12 inclusive.
Face values may repeat, both within a die and across dice.
We define the 'beats' relationship between two dice to be the following:
A has a strictly larger face value than die B in more than half of all possible pairs of faces.

Print the dice (dice) as a list of lists where each sublist is a die; row 0 is Rock, row 1 is Paper, row 2 is Scissors, row 3 is Lizard, and row 4 is Spock.
