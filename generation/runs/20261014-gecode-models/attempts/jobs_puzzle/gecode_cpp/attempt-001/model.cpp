#include "dcp.h"

// Jobs puzzle: four people each hold exactly two of eight different jobs.
// Output: the person (0-3) holding each job.
class JobsPuzzle : public dcp::Space {
 protected:
  // holder[j]: person holding job j, with the jobs in the order below
  IntVarArray holder;

  static const int CHEF = 0, GUARD = 1, NURSE = 2, CLERK = 3,
                   POLICE = 4, TEACHER = 5, ACTOR = 6, BOXER = 7;

 public:
  explicit JobsPuzzle(const json& instance) : holder(*this, 8, 0, 3) {
    (void)instance;  // the puzzle has no instance data

    // each person holds exactly two jobs
    for (int p = 0; p < 4; ++p) count(*this, holder, p, IRT_EQ, 2);

    // clue 1: the nurse is not a teacher, police officer, or clerk
    rel(*this, holder[NURSE], IRT_NQ, holder[TEACHER]);
    rel(*this, holder[NURSE], IRT_NQ, holder[POLICE]);
    rel(*this, holder[NURSE], IRT_NQ, holder[CLERK]);

    // clue 2: the clerk is not the chef
    rel(*this, holder[CLERK], IRT_NQ, holder[CHEF]);

    // clue 3: person 0 is not the boxer
    rel(*this, holder[BOXER], IRT_NQ, 0);

    // clue 4: person 3 is not the teacher, police officer, or nurse
    rel(*this, holder[TEACHER], IRT_NQ, 3);
    rel(*this, holder[POLICE], IRT_NQ, 3);
    rel(*this, holder[NURSE], IRT_NQ, 3);

    // clue 5: person 0, the chef, and the police officer went golfing together,
    // so they are three different people
    rel(*this, holder[CHEF], IRT_NQ, 0);
    rel(*this, holder[POLICE], IRT_NQ, 0);
    rel(*this, holder[CHEF], IRT_NQ, holder[POLICE]);

    branch(*this, holder, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("actor", holder[ACTOR]);
    output("boxer", holder[BOXER]);
    output("chef", holder[CHEF]);
    output("clerk", holder[CLERK]);
    output("guard", holder[GUARD]);
    output("nurse", holder[NURSE]);
    output("police_officer", holder[POLICE]);
    output("teacher", holder[TEACHER]);
  }

  JobsPuzzle(JobsPuzzle& s) : dcp::Space(s) { holder.update(*this, s.holder); }
  Gecode::Space* copy() override { return new JobsPuzzle(*this); }
};

DCP_MODEL(JobsPuzzle)
