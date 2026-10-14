#include "dcp.h"

// Males and females enter a room one at a time. Find an entry order in which the
// ratio of females to males in the room is never greater than 7/3 at any time.
// 13 people, of whom 4 are male and 9 female. The output sequence lists each entrant
// as 0 for male and 1 for female, in entry order.
class PeopleInARoom : public dcp::Space {
 protected:
  // seq[i] = 1 if the i-th person to enter is female, 0 if male
  BoolVarArray seq;

 public:
  // The instance has no fields: the numbers come from the problem statement.
  explicit PeopleInARoom(const json& instance) {
    (void)instance;
    const int people = 13;
    const int males = 4;
    const int females = people - males;  // 9

    seq = BoolVarArray(*this, people, 0, 1);

    // 4 of the 13 people are male, so 9 are female
    linear(*this, seq, IRT_EQ, females);

    // at any time the room holds k people, of whom F are female and k - F are male.
    // The ratio F / (k - F) must not exceed 7/3, i.e. 3F <= 7(k - F), i.e. F <= 7k/10.
    // Checked after every entry, so the first person to enter must be male.
    for (int k = 1; k <= people; ++k) {
      BoolVarArgs room;
      for (int i = 0; i < k; ++i) room << seq[i];
      linear(*this, room, IRT_LQ, 7 * k / 10);
    }

    // branch on the entry order, trying male first
    branch(*this, seq, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("sequence", seq);
  }

  PeopleInARoom(PeopleInARoom& s) : dcp::Space(s) { seq.update(*this, s.seq); }
  Gecode::Space* copy() override { return new PeopleInARoom(*this); }
};

DCP_MODEL(PeopleInARoom)
