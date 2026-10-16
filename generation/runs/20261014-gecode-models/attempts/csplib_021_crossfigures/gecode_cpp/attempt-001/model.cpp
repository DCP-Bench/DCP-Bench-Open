#include "dcp.h"

// Crossfigures (CSPLib 021): place a digit in every white cell of a 9x9 grid so
// that each maximal run of white cells, read across or down, is a number with
// no leading zero, and each clue holds for the number of its entry.
// The problem fixes the grid and the clues, so the instance has no fields.
class Crossfigures : public dcp::Space {
 protected:
  IntVarArray cell;  // cell[9*r + c]: digit of row r, column c (0-based); black cells are 0

  // the digits at the positions cs (read in order) form the number v
  void link(const std::vector<int>& cs, IntVar v) {
    IntVarArgs digits;
    IntArgs weight;
    int p = 1;
    for (int k = static_cast<int>(cs.size()) - 1; k >= 0; --k) {
      digits << cell[cs[k]];
      weight << p;
      p *= 10;
    }
    linear(*this, weight, digits, IRT_EQ, v, IPL_DOM);
  }

  // a number of the length of cs, with no leading zero
  IntVar number(const std::vector<int>& cs) {
    int lo = 1;
    for (std::size_t k = 1; k < cs.size(); ++k) lo *= 10;
    IntVar v(*this, lo, 10 * lo - 1);
    link(cs, v);
    return v;
  }

  // the cells of an across entry starting at (r, c), 1-based, of length len
  static std::vector<int> across(int r, int c, int len) {
    std::vector<int> cs;
    for (int k = 0; k < len; ++k) cs.push_back((r - 1) * 9 + (c - 1) + k);
    return cs;
  }

  // the cells of a down entry starting at (r, c), 1-based, of length len
  static std::vector<int> down(int r, int c, int len) {
    std::vector<int> cs;
    for (int k = 0; k < len; ++k) cs.push_back((r - 1 + k) * 9 + (c - 1));
    return cs;
  }

 public:
  explicit Crossfigures(const json& instance) {
    (void)instance;
    cell = IntVarArray(*this, 81, 0, 9);

    // black cells hold no digit
    const int black[] = {4, 11, 15, 19, 22, 25, 31, 36, 38, 39, 40, 41, 42, 44,
                         49, 55, 58, 61, 65, 69, 76};
    for (int i : black) rel(*this, cell[i], IRT_EQ, 0);

    // across entries
    IntVar A1 = number(across(1, 1, 4));
    IntVar A4 = number(across(1, 6, 4));
    IntVar A7 = number(across(2, 1, 2));
    IntVar A8 = number(across(2, 4, 3));
    IntVar A9 = number(across(2, 8, 2));
    IntVar A10 = number(across(3, 3, 2));
    IntVar A11 = number(across(3, 6, 2));
    IntVar A13 = number(across(4, 1, 4));
    IntVar A15 = number(across(4, 6, 4));
    IntVar A17 = number(across(6, 1, 4));
    IntVar A20 = number(across(6, 6, 4));
    // 23 across: a prime number, two digits
    IntVar A23(*this, IntSet({11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
                              71, 73, 79, 83, 89, 97}));
    link(across(7, 3, 2), A23);
    IntVar A24 = number(across(7, 6, 2));
    IntVar A25 = number(across(8, 1, 2));
    IntVar A27 = number(across(8, 4, 3));
    IntVar A28 = number(across(8, 8, 2));
    IntVar A29 = number(across(9, 1, 4));
    IntVar A30 = number(across(9, 6, 4));

    // down entries
    IntVar D1 = number(down(1, 1, 4));
    IntVar D2 = number(down(1, 2, 2));
    IntVar D3 = number(down(1, 4, 4));
    IntVar D4 = number(down(1, 6, 4));
    IntVar D5 = number(down(1, 8, 2));
    IntVar D6 = number(down(1, 9, 4));
    IntVar D10 = number(down(3, 3, 2));
    IntVar D12 = number(down(3, 7, 2));
    IntVar D14 = number(down(4, 2, 3));
    IntVar D16 = number(down(4, 8, 3));
    IntVar D17 = number(down(6, 1, 4));
    IntVar D18 = number(down(6, 3, 2));
    IntVar D19 = number(down(6, 4, 4));
    IntVar D20 = number(down(6, 6, 4));
    IntVar D21 = number(down(6, 7, 2));
    IntVar D22 = number(down(6, 9, 4));
    IntVar D26 = number(down(8, 2, 2));
    IntVar D28 = number(down(8, 8, 2));

    // 20 across: a square number (its root is 32..99 for four digits)
    IntVar s20(*this, 32, 99);
    rel(*this, s20 * s20 == A20);
    // 24 across: a square number (its root is 4..9 for two digits)
    IntVar s24(*this, 4, 9);
    rel(*this, s24 * s24 == A24);

    // clue 1 across: 27 across times two
    rel(*this, A1 == 2 * A27);
    // clue 4 across: 4 down plus seventy-one
    rel(*this, A4 == D4 + 71);
    // clue 7 across: 18 down plus four
    rel(*this, A7 == D18 + 4);
    // clue 8 across: 6 down divided by sixteen
    rel(*this, D6 == 16 * A8);
    // clue 9 across: 2 down minus eighteen
    rel(*this, A9 == D2 - 18);
    // clue 10 across: dozen in six gross (6 * 144 / 12)
    rel(*this, A10, IRT_EQ, 72);
    // clue 11 across: 5 down minus seventy
    rel(*this, A11 == D5 - 70);
    // clue 13 across: 26 down times 23 across
    rel(*this, A13 == D26 * A23);
    // clue 15 across: 6 down minus 350
    rel(*this, A15 == D6 - 350);
    // clue 17 across: 25 across times 23 across
    rel(*this, A17 == A25 * A23);
    // clue 25 across: 20 across divided by seventeen
    rel(*this, A20 == 17 * A25);
    // clue 27 across: 6 down divided by four
    rel(*this, D6 == 4 * A27);
    // clue 28 across: four dozen (4 * 12)
    rel(*this, A28, IRT_EQ, 48);
    // clue 29 across: seven gross (7 * 144)
    rel(*this, A29, IRT_EQ, 1008);
    // clue 30 across: 22 down plus 450
    rel(*this, A30 == D22 + 450);

    // clue 1 down: 1 across plus twenty-seven
    rel(*this, D1 == A1 + 27);
    // clue 2 down: five dozen (5 * 12)
    rel(*this, D2, IRT_EQ, 60);
    // clue 3 down: 30 across plus 888
    rel(*this, D3 == A30 + 888);
    // clue 4 down: two times 17 across
    rel(*this, D4 == 2 * A17);
    // clue 5 down: 29 across divided by twelve
    rel(*this, A29 == 12 * D5);
    // clue 6 down: 28 across times 23 across
    rel(*this, D6 == A28 * A23);
    // clue 10 down: 10 across plus four
    rel(*this, D10 == A10 + 4);
    // clue 12 down: three times 24 across
    rel(*this, D12 == 3 * A24);
    // clue 14 down: 13 across divided by sixteen
    rel(*this, A13 == 16 * D14);
    // clue 16 down: 28 down times fifteen
    rel(*this, D16 == 15 * D28);
    // clue 17 down: 13 across minus 399
    rel(*this, D17 == A13 - 399);
    // clue 18 down: 29 across divided by eighteen
    rel(*this, A29 == 18 * D18);
    // clue 19 down: 22 down minus ninety-four
    rel(*this, D19 == D22 - 94);
    // clue 20 down: 20 across minus nine
    rel(*this, D20 == A20 - 9);
    // clue 21 down: 25 across minus fifty-two
    rel(*this, D21 == A25 - 52);
    // clue 22 down: 20 down times six
    rel(*this, D22 == 6 * D20);
    // clue 26 down: five times 24 across
    rel(*this, D26 == 5 * A24);
    // clue 28 down: 21 down plus twenty-seven
    rel(*this, D28 == D21 + 27);

    // branch on every digit, then on the square roots
    branch(*this, cell, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    IntVarArgs roots;
    roots << s20 << s24;
    branch(*this, roots, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    Matrix<IntVarArray> M(cell, 9, 9);
    output("M", M);
  }

  Crossfigures(Crossfigures& s) : dcp::Space(s) { cell.update(*this, s.cell); }
  Gecode::Space* copy() override { return new Crossfigures(*this); }
};

DCP_MODEL(Crossfigures)
