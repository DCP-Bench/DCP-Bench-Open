# Jobs puzzle
Four people, eight jobs, each person holds exactly two jobs, so each job has exactly one holder.
Encoding: one-hot per job over the holder (person 0..3), `h[job][p]`.
- Each job is held by exactly one person -> `sum_p h[job][p] == 1`.
- Each person holds exactly two jobs -> `sum_job h[job][p] == 2`.
- Clue 1: the nurse is not a teacher, police officer, or clerk -> for each person p: not (nurse and X) for X in teacher, police officer, clerk.
- Clue 2: the clerk is not the chef -> for each person p: not (clerk and chef).
- Clue 3: person 0 is not the boxer -> `~h[boxer][0]`.
- Clue 4: person 3 is not the teacher, police officer, or nurse -> `~h[teacher][3]`, `~h[police_officer][3]`, `~h[nurse][3]`.
- Clue 5: person 0, the chef, and the police officer went golfing together -> three distinct people: person 0 is not the chef and not the police officer, and the chef and police officer are different people.
- Output: per job, the person index `sum_p p * h[job][p]`.
- Objective: satisfaction.
