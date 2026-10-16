#include "dcp.h"

// Queue of ten people, each with initials that are an alphabetically ordered
// pair of distinct letters from A..E, so letters are 0..4 with first < second.
// All ten initials are different, no-one shares a letter with the person in
// front of them, and the front three are BE, CD and the last person is BD.
class InitialsQueue : public dcp::Space {
 protected:
  static const int people = 10;   // problem constant: ten people in the queue
  static const int letters = 5;   // problem constant: letters A..E, coded 0..4
  IntVarArray first;              // first[i]: first letter of person i's initials
  IntVarArray second;             // second[i]: second letter of person i's initials
  IntVarArray pair;               // pair[i] = 5 * first[i] + second[i], a code for the pair

 public:
  explicit InitialsQueue(const json& instance) {
    (void)instance;  // the problem has no instance fields; all data is in the statement
    first = IntVarArray(*this, people, 0, letters - 1);
    second = IntVarArray(*this, people, 0, letters - 1);
    pair = IntVarArray(*this, people, 0, letters * letters - 1);

    // initials are an alphabetically ordered pair of distinct letters
    for (int i = 0; i < people; ++i) {
      rel(*this, first[i] < second[i]);
      rel(*this, pair[i] == 5 * first[i] + second[i]);
    }

    // all ten initials are different
    distinct(*this, pair, IPL_DOM);

    // no-one shares a letter with the person in front of them
    for (int i = 0; i + 1 < people; ++i) {
      rel(*this, first[i] != first[i + 1]);
      rel(*this, first[i] != second[i + 1]);
      rel(*this, second[i] != first[i + 1]);
      rel(*this, second[i] != second[i + 1]);
    }

    // BE at the front of the queue
    rel(*this, first[0] == 1);
    rel(*this, second[0] == 4);

    // CD right behind BE
    rel(*this, first[1] == 2);
    rel(*this, second[1] == 3);

    // BD right at the end of the queue
    rel(*this, first[people - 1] == 1);
    rel(*this, second[people - 1] == 3);

    branch(*this, first, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, second, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // output: the queue from the front, one [first, second] pair per person
    std::vector<IntVarArgs> queue(people);
    for (int i = 0; i < people; ++i) queue[i] << first[i] << second[i];
    output("queue", queue);
  }

  InitialsQueue(InitialsQueue& s) : dcp::Space(s) {
    first.update(*this, s.first);
    second.update(*this, s.second);
    pair.update(*this, s.pair);
  }
  Gecode::Space* copy() override { return new InitialsQueue(*this); }
};

DCP_MODEL(InitialsQueue)
