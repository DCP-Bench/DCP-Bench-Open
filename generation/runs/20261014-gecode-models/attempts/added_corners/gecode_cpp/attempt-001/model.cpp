#include "dcp.h"

// Added corners: place the digits 1 to 8 in the 8 positions of a 3x3 frame
// with the centre removed. Four positions are circles (the corners) and four
// are squares (the edge midpoints). Each square holds the sum of the two
// circles adjoining it. Positions are numbered in reading order:
//   0 1 2
//   3   4
//   5 6 7
// Circles: 0, 2, 5, 7. Squares: 1, 3, 4, 6.
class AddedCorners : public dcp::Space {
 protected:
  IntVarArray p;  // p[i]: digit in position i, reading order

 public:
  // The puzzle has a fixed layout and no instance data, so the constructor
  // ignores its argument.
  explicit AddedCorners(const json& /*instance*/) : p(*this, 8, 1, 8) {
    // the digits 1 through 8 are each used once
    distinct(*this, p, IPL_DOM);

    // the four circles are the corners: together they make half of the
    // digit total (1+...+8 = 36), and each square counts twice, so the
    // circles sum to 12
    IntVarArgs circles;
    circles << p[0] << p[2] << p[5] << p[7];
    linear(*this, circles, IRT_EQ, 12, IPL_DOM);

    // top square = top-left circle + top-right circle
    rel(*this, p[0] + p[2] == p[1]);

    // left square = top-left circle + bottom-left circle
    rel(*this, p[0] + p[5] == p[3]);

    // right square = top-right circle + bottom-right circle
    rel(*this, p[2] + p[7] == p[4]);

    // bottom square = bottom-left circle + bottom-right circle
    rel(*this, p[5] + p[7] == p[6]);

    branch(*this, p, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("positions", p);
  }

  AddedCorners(AddedCorners& s) : dcp::Space(s) { p.update(*this, s.p); }
  Gecode::Space* copy() override { return new AddedCorners(*this); }
};

DCP_MODEL(AddedCorners)
