Four people hold eight different jobs -> holder[job] in 0..3 for each of the 8 jobs (one holder per job), output per job
Each person holds exactly two jobs -> count(*this, holder, p, IRT_EQ, 2) for p = 0..3
The nurse is not a teacher -> rel(*this, nurse, IRT_NQ, teacher)
The nurse is not a police officer -> rel(*this, nurse, IRT_NQ, police_officer)
The nurse is not a clerk -> rel(*this, nurse, IRT_NQ, clerk)
The clerk is not the chef -> rel(*this, clerk, IRT_NQ, chef)
Person 0 is not the boxer -> rel(*this, boxer, IRT_NQ, 0)
Person 3 is not the teacher, police officer, or nurse -> rel(*this, teacher, IRT_NQ, 3), rel(police_officer, IRT_NQ, 3), rel(nurse, IRT_NQ, 3)
Person 0, the chef, and the police officer went golfing together (three distinct people) -> rel(chef, IRT_NQ, 0), rel(police_officer, IRT_NQ, 0), rel(chef, IRT_NQ, police_officer)
Branching -> branch(*this, holder, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) (small domains, 8 variables; no objective)
Objective -> none (satisfaction)
