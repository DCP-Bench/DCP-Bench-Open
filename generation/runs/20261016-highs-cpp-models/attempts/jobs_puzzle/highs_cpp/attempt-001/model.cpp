// jobs_puzzle: four people hold eight different jobs, each person holds exactly two jobs.
// Clues: nurse is not teacher, police officer or clerk; clerk is not chef; person 0 is not
// the boxer; person 3 is not teacher, police officer or nurse; person 0, the chef and the
// police officer went golfing together. Output: the person index for each job.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // Jobs and persons are numbered 0..7 and 0..3 as in the description's list.
  // Job order: chef 0, guard 1, nurse 2, clerk 3, police_officer 4, teacher 5, actor 6, boxer 7.
  const int NJOBS = 8;
  const int NPEOPLE = 4;
  const int CHEF = 0, GUARD = 1, NURSE = 2, CLERK = 3, POLICE = 4, TEACHER = 5, ACTOR = 6, BOXER = 7;

  // x[j][p] = 1 when person p holds job j.
  std::vector<std::vector<dcp::Lin>> x(NJOBS, std::vector<dcp::Lin>(NPEOPLE));
  for (int j = 0; j < NJOBS; ++j)
    for (int p = 0; p < NPEOPLE; ++p) x[j][p] = dcp::new_var(h, 0, 1);

  // each job is held by exactly one person
  for (int j = 0; j < NJOBS; ++j) {
    dcp::Lin holders;
    for (int p = 0; p < NPEOPLE; ++p) holders = holders + x[j][p];
    dcp::add_row(h, holders, 1, 1);
  }

  // each person holds exactly two jobs
  for (int p = 0; p < NPEOPLE; ++p) {
    dcp::Lin held;
    for (int j = 0; j < NJOBS; ++j) held = held + x[j][p];
    dcp::add_row(h, held, 2, 2);
  }

  // the nurse is not a teacher, police officer, or clerk (no person holds both)
  for (int p = 0; p < NPEOPLE; ++p) {
    dcp::add_row(h, x[NURSE][p] + x[TEACHER][p], -kHighsInf, 1);
    dcp::add_row(h, x[NURSE][p] + x[POLICE][p], -kHighsInf, 1);
    dcp::add_row(h, x[NURSE][p] + x[CLERK][p], -kHighsInf, 1);
  }

  // the clerk is not the chef (no person holds both)
  for (int p = 0; p < NPEOPLE; ++p)
    dcp::add_row(h, x[CLERK][p] + x[CHEF][p], -kHighsInf, 1);

  // person 0 is not the boxer
  dcp::add_row(h, x[BOXER][0], 0, 0);

  // person 3 is not the teacher, police officer, or nurse
  dcp::add_row(h, x[TEACHER][3], 0, 0);
  dcp::add_row(h, x[POLICE][3], 0, 0);
  dcp::add_row(h, x[NURSE][3], 0, 0);

  // person 0, the chef, and the police officer went golfing together:
  // three different people, so person 0 is neither the chef nor the police officer,
  // and the chef and the police officer are different people
  dcp::add_row(h, x[CHEF][0], 0, 0);
  dcp::add_row(h, x[POLICE][0], 0, 0);
  for (int p = 0; p < NPEOPLE; ++p)
    dcp::add_row(h, x[CHEF][p] + x[POLICE][p], -kHighsInf, 1);

  // outputs: the person index holding each job
  auto holder = [&](int j) {
    dcp::Lin idx;
    for (int p = 0; p < NPEOPLE; ++p) idx = idx + static_cast<double>(p) * x[j][p];
    return idx;
  };
  out.add("actor", holder(ACTOR));
  out.add("boxer", holder(BOXER));
  out.add("chef", holder(CHEF));
  out.add("clerk", holder(CLERK));
  out.add("guard", holder(GUARD));
  out.add("nurse", holder(NURSE));
  out.add("police_officer", holder(POLICE));
  out.add("teacher", holder(TEACHER));
}
