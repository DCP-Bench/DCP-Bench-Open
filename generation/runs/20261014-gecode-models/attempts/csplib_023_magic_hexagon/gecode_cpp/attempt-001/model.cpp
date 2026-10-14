#include "dcp.h"

// Magic hexagon: place the numbers 1 to NUM_CELLS (19) in the 19 cells of a
// hexagon, A B C / D E F G / H I J K L / M N O P / Q R S, so that every one of
// the 15 lines (3 rows, 5 down-left diagonals, 5 down-right diagonals) sums to
// the magic constant MAGIC_SUM (38).
class MagicHexagon : public dcp::Space {
 protected:
  IntVarArray LD;  // LD[k]: number in cell k, cells read A..S

 public:
  explicit MagicHexagon(const json& instance) {
    int n = instance.at("NUM_CELLS").get<int>();
    int magic = instance.at("MAGIC_SUM").get<int>();

    LD = IntVarArray(*this, n, 1, n);

    // all the numbers 1 to n are different, so each appears once
    distinct(*this, LD, IPL_DOM);

    // the three horizontal rows: A B C, D E F G, H I J K L, M N O P, Q R S
    const int rows[5][5] = {
        {0, 1, 2, -1, -1},
        {3, 4, 5, 6, -1},
        {7, 8, 9, 10, 11},
        {12, 13, 14, 15, -1},
        {16, 17, 18, -1, -1}};
    const int row_len[5] = {3, 4, 5, 4, 3};
    for (int r = 0; r < 5; ++r) {
      IntVarArgs line;
      for (int c = 0; c < row_len[r]; ++c) line << LD[rows[r][c]];
      linear(*this, line, IRT_EQ, magic, IPL_DOM);
    }

    // the five diagonals running down and to the left: A D H, B E I M,
    // C F J N Q, G K O R, L P S
    const int down_left[5][5] = {
        {0, 3, 7, -1, -1},
        {1, 4, 8, 12, -1},
        {2, 5, 9, 13, 16},
        {6, 10, 14, 17, -1},
        {11, 15, 18, -1, -1}};
    const int dl_len[5] = {3, 4, 5, 4, 3};
    for (int d = 0; d < 5; ++d) {
      IntVarArgs line;
      for (int c = 0; c < dl_len[d]; ++c) line << LD[down_left[d][c]];
      linear(*this, line, IRT_EQ, magic, IPL_DOM);
    }

    // the five diagonals running down and to the right: C G L, B F K P,
    // A E J O S, D I N R, H M Q
    const int down_right[5][5] = {
        {2, 6, 11, -1, -1},
        {1, 5, 10, 15, -1},
        {0, 4, 9, 14, 18},
        {3, 8, 13, 17, -1},
        {7, 12, 16, -1, -1}};
    const int dr_len[5] = {3, 4, 5, 4, 3};
    for (int d = 0; d < 5; ++d) {
      IntVarArgs line;
      for (int c = 0; c < dr_len[d]; ++c) line << LD[down_right[d][c]];
      linear(*this, line, IRT_EQ, magic, IPL_DOM);
    }

    // branch on every cell, the most constrained first
    branch(*this, LD, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("LD", LD);
  }

  MagicHexagon(MagicHexagon& s) : dcp::Space(s) { LD.update(*this, s.LD); }
  Gecode::Space* copy() override { return new MagicHexagon(*this); }
};

DCP_MODEL(MagicHexagon)
