#include "dcp.h"

// Golomb ruler: place m marks on a line so that all distances between two marks
// are different, and minimise the position of the last mark (the length).
class GolombRuler : public dcp::Space {
 protected:
  IntVarArray marks;  // marks[i]: position of mark i, marks[0] = 0
  IntVar length;      // position of the last mark

 public:
  explicit GolombRuler(const json& instance) {
    int m = instance.at("size").get<int>();

    // Upper bound on any mark. The Erdos-Turan construction with a prime p
    // between m and 2m (Bertrand) gives a ruler of length below 2p^2 <= 8m^2
    // (a domain bound the problem does not state; it is not a constraint).
    int top = 8 * m * m;
    marks = IntVarArray(*this, m, 0, top);

    // the first mark is at 0
    rel(*this, marks[0] == 0);

    // marks are in increasing order: a_1 < a_2 < ... < a_m
    for (int i = 0; i + 1 < m; ++i) rel(*this, marks[i], IRT_LE, marks[i + 1]);

    // the m(m-1)/2 differences a_j - a_i (i < j) are all different
    IntVarArgs differences;
    for (int i = 0; i < m; ++i)
      for (int j = i + 1; j < m; ++j) differences << expr(*this, marks[j] - marks[i]);
    distinct(*this, differences, IPL_DOM);

    // the length is the position of the last mark
    length = marks[m - 1];

    // build the ruler from the first mark on, smallest position first
    branch(*this, marks, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(length);
    output("marks", marks);
    output("length", length);
  }

  GolombRuler(GolombRuler& s) : dcp::Space(s) {
    marks.update(*this, s.marks);
    length.update(*this, s.length);
  }
  Gecode::Space* copy() override { return new GolombRuler(*this); }
};

DCP_MODEL(GolombRuler)
