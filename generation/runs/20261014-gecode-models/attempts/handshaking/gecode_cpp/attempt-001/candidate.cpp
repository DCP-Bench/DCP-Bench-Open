#include "dcp.h"

// Handshaking (Halmos): Hilary and Jocelyn are married and invite n couples who are
// friends. Everybody shakes hands with others, never with self or with their spouse.
// Jocelyn then asks everybody except herself how many hands they have shaken, and
// all answers are different. Output the number of hands Hilary has shaken.
class Handshaking : public dcp::Space {
 protected:
  int n;               // number of invited couples
  int people;          // 2n+2: 0 = Jocelyn, 1 = Hilary, then the invited couples
  BoolVarArray shake;  // one Boolean per pair i < j: did i and j shake hands
  IntVarArray hands;   // hands[i]: number of hands person i has shaken

  // Position of the handshake between persons i and j in the upper triangle.
  static int pair_index(int people, int i, int j) {
    if (i > j) {
      int t = i;
      i = j;
      j = t;
    }
    return i * (2 * people - i - 1) / 2 + (j - i - 1);
  }

 public:
  explicit Handshaking(const json& instance) {
    n = instance.at("num_couples").get<int>();
    people = 2 * n + 2;
    shake = BoolVarArray(*this, people * (people - 1) / 2, 0, 1);
    hands = IntVarArray(*this, people, 0, people - 2);

    // Hilary and Jocelyn are married, so they do not shake hands
    rel(*this, shake[pair_index(people, 0, 1)], IRT_EQ, 0);

    // each invited couple: nobody shakes hands with his or her spouse
    for (int k = 0; k < n; ++k) {
      int a = 2 + 2 * k;
      int b = 3 + 2 * k;
      rel(*this, shake[pair_index(people, a, b)], IRT_EQ, 0);
    }

    // hands[i] is the number of handshakes that involve person i
    for (int i = 0; i < people; ++i) {
      BoolVarArgs row;
      for (int j = 0; j < people; ++j)
        if (j != i) row << shake[pair_index(people, i, j)];
      rel(*this, sum(row) == hands[i]);
    }

    // all the answers are different: everybody except Jocelyn was asked
    IntVarArgs answers;
    for (int i = 1; i < people; ++i) answers << hands[i];
    distinct(*this, answers, IPL_DOM);

    // implied: the answers are 0..2n, so the guest with 2n hands shook everybody but
    // his or her spouse, which makes the spouse the guest with 0 hands; removing that
    // couple and repeating gives that each invited couple's answers sum to 2n.
    // (Derived from the problem, it prunes the search; the evaluator checks the result.)
    for (int k = 0; k < n; ++k)
      rel(*this, hands[2 + 2 * k] + hands[3 + 2 * k] == 2 * n);

    branch(*this, answers, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, shake, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("hil", hands[1]);
  }

  Handshaking(Handshaking& s) : dcp::Space(s), n(s.n), people(s.people) {
    shake.update(*this, s.shake);
    hands.update(*this, s.hands);
  }
  Gecode::Space* copy() override { return new Handshaking(*this); }
};

DCP_MODEL(Handshaking)
