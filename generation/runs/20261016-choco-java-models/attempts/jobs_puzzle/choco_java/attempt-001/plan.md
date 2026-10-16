Problem: four people (0-3), eight different jobs, each person holds exactly two jobs; each job held by one person.
- each job held by exactly one person -> sum over persons of x[p][j] = 1
- each person holds exactly two jobs -> sum over jobs of x[p][j] = 2
- Clue 1: nurse not teacher, police officer, or clerk -> x[p][nurse] + x[p][j] <= 1 for each p
- Clue 2: clerk not chef -> x[p][clerk] + x[p][chef] <= 1
- Clue 3: person 0 not boxer -> x[0][boxer] = 0
- Clue 4: person 3 not teacher, police officer, nurse -> x[3][...] = 0
- Clue 5: person 0, the chef, and the police officer went golfing together -> three different people: x[0][chef] = x[0][police] = 0 and chef and police held by different people
- output: each job's person index = sum_p p * x[p][j]
Objective: none (satisfaction).
