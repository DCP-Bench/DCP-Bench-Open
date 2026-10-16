// Jobs puzzle: four people (0 to 3) hold eight different jobs, two each. Find which person holds
// each job, from the clues:
//  1. the nurse is not a teacher, police officer or clerk (different people hold them)
//  2. the clerk is not the chef
//  3. person 0 is not the boxer
//  4. person 3 is not the teacher, police officer or nurse
//  5. person 0, the chef and the police officer went golfing together: three different people
// Each job variable holds the person who has it.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the person holding each job; the jobs are numbered in the order of the output names
  IntVar* actor = newIntVar(0, 3);
  IntVar* boxer = newIntVar(0, 3);
  IntVar* chef = newIntVar(0, 3);
  IntVar* clerk = newIntVar(0, 3);
  IntVar* guard = newIntVar(0, 3);
  IntVar* nurse = newIntVar(0, 3);
  IntVar* police = newIntVar(0, 3);
  IntVar* teacher = newIntVar(0, 3);
  vec<IntVar*> jobs;
  jobs.push(actor);
  jobs.push(boxer);
  jobs.push(chef);
  jobs.push(clerk);
  jobs.push(guard);
  jobs.push(nurse);
  jobs.push(police);
  jobs.push(teacher);

  // each person holds exactly two of the jobs
  for (int p = 0; p < 4; ++p) {
    vec<BoolView> holds;
    for (int j = 0; j < 8; ++j) {
      BoolView b = newBoolVar();
      int_rel_reif(jobs[j], IRT_EQ, p, b);
      holds.push(b);
    }
    bool_linear(holds, IRT_EQ, getConstant(2));
  }

  // clue 1: the nurse is not a teacher, police officer or clerk
  int_rel(nurse, IRT_NE, teacher);
  int_rel(nurse, IRT_NE, police);
  int_rel(nurse, IRT_NE, clerk);

  // clue 2: the clerk is not the chef
  int_rel(clerk, IRT_NE, chef);

  // clue 3: person 0 is not the boxer
  int_rel(boxer, IRT_NE, 0);

  // clue 4: person 3 is not the teacher, police officer or nurse
  int_rel(teacher, IRT_NE, 3);
  int_rel(police, IRT_NE, 3);
  int_rel(nurse, IRT_NE, 3);

  // clue 5: person 0, the chef and the police officer are three different people
  int_rel(chef, IRT_NE, 0);
  int_rel(police, IRT_NE, 0);
  int_rel(chef, IRT_NE, police);

  // the holders of the jobs are the decision variables
  branch(jobs, VAR_INORDER, VAL_MIN);

  outputs = {{"actor", dcp::out(actor)},     {"boxer", dcp::out(boxer)},
             {"chef", dcp::out(chef)},       {"clerk", dcp::out(clerk)},
             {"guard", dcp::out(guard)},     {"nurse", dcp::out(nurse)},
             {"police_officer", dcp::out(police)}, {"teacher", dcp::out(teacher)}};
}
