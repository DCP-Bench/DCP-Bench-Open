#include "dcp.h"

// Crossword: complete the 6 x 5 grid by selecting 8 of the 15 given words, one
// per entry, so that every entry is filled and crossing cells agree.
//
// The grid and word list are part of the problem statement and are fixed here.
// Grid rows r0..r5 and columns c0..c4 ('#' is a block):
//   r0: . . . . .
//   r1: # # . # .
//   r2: # . . . .
//   r3: . # . . .
//   r4: . . . . .
//   r5: . # # . #
// Entries, numbered as in the statement: 1 across (r0, c0..c4), 2 down (c2, r0..r4),
// 3 down (c4, r0..r4), 4 across (r2, c1..c4), 5 down (c3, r2..r5), 6 down (c0, r3..r5),
// 7 across (r3, c2..c4), 8 across (r4, c0..c4).
// Words, sorted by length (longest first) and then alphabetically, are indexed 0..14.

namespace {

const char* kGrid[6] = {".....", "##.#.", "#....", ".#...", ".....", ".##.#"};

const char* kWords[15] = {"HOSES", "LASER", "SAILS", "SHEET", "STEER",
                          "HEEL",  "HIKE",  "KEEL",  "KNOT",  "LINE",
                          "AFT",   "ALE",   "EEL",   "LEE",   "TIE"};

struct Entry {
  int row, col, dr, dc, len;
};

// Entries 1..8 in statement order.
const Entry kEntries[8] = {
    {0, 0, 0, 1, 5},  // 1 across
    {0, 2, 1, 0, 5},  // 2 down
    {0, 4, 1, 0, 5},  // 3 down
    {2, 1, 0, 1, 4},  // 4 across
    {2, 3, 1, 0, 4},  // 5 down
    {3, 0, 1, 0, 3},  // 6 down
    {3, 2, 0, 1, 3},  // 7 across
    {4, 0, 0, 1, 5},  // 8 across
};

}  // namespace

class Crossword : public dcp::Space {
 protected:
  IntVarArray entry;  // entry[k]: index of the word filling entry k+1
  IntVarArray letter; // letter[id]: letter (0..25) of each open grid cell

 public:
  explicit Crossword(const json& instance) {
    (void)instance;  // the puzzle is fixed by the statement; the instance has no fields

    // map each open cell to a variable id
    int id[6][5];
    int open = 0;
    for (int r = 0; r < 6; ++r)
      for (int c = 0; c < 5; ++c) id[r][c] = kGrid[r][c] == '.' ? open++ : -1;
    letter = IntVarArray(*this, open, 0, 25);

    // each entry is one of the words of its length
    entry = IntVarArray(*this, 8, 0, 14);
    for (int k = 0; k < 8; ++k) {
      std::vector<int> candidates;
      for (int w = 0; w < 15; ++w)
        if (static_cast<int>(std::string(kWords[w]).size()) == kEntries[k].len)
          candidates.push_back(w);
      IntSet domain(candidates.data(), static_cast<int>(candidates.size()));
      dom(*this, entry[k], domain);
    }

    // the letters of the chosen word fill the cells of its entry, and a cell
    // shared by two entries takes one letter for both
    for (int k = 0; k < 8; ++k) {
      const Entry& e = kEntries[k];
      for (int p = 0; p < e.len; ++p) {
        IntArgs table(15);
        for (int w = 0; w < 15; ++w) {
          std::string word = kWords[w];
          table[w] = p < static_cast<int>(word.size()) ? word[p] - 'A' : 0;
        }
        int cell = id[e.row + e.dr * p][e.col + e.dc * p];
        element(*this, table, entry[k], letter[cell], IPL_DOM);
      }
    }

    // the 8 selected words are different words
    distinct(*this, entry, IPL_DOM);

    branch(*this, entry, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, letter, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("E", entry);
  }

  Crossword(Crossword& s) : dcp::Space(s) {
    entry.update(*this, s.entry);
    letter.update(*this, s.letter);
  }
  Gecode::Space* copy() override { return new Crossword(*this); }
};

DCP_MODEL(Crossword)
