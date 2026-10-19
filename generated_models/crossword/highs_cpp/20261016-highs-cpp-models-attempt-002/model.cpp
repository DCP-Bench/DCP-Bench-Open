// Crossword: complete the puzzle grid (6 rows, 5 columns, '#' cells are blocks) by
// selecting 8 of the 15 listed words, one per numbered word slot, so that crossing letters agree.
// Output E: E[i] is the index of the word that starts at location number i+1.
#include <map>
#include <string>
#include <utility>
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;
  using dcp::Lin;
  using dcp::add_row;
  using dcp::new_var;

  // The 15 words, sorted by length (longest first) and then alphabetically; index = position.
  const std::vector<std::string> words = {
      "HOSES", "LASER", "SAILS", "SHEET", "STEER",  // 5 letters: 0..4
      "HEEL",  "HIKE",  "KEEL",  "KNOT",  "LINE",   // 4 letters: 5..9
      "AFT",   "ALE",   "EEL",   "LEE",   "TIE"};   // 3 letters: 10..14
  const int W = static_cast<int>(words.size());

  // The word slots of the grid, as (row, column) cells, 0-based, in the order of the puzzle
  // numbers 1..8 (the locations where a word starts).
  const std::vector<std::vector<std::pair<int, int>>> slots = {
      {{0, 0}, {0, 1}, {0, 2}, {0, 3}, {0, 4}},  // 1 across
      {{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 2}},  // 2 down
      {{0, 4}, {1, 4}, {2, 4}, {3, 4}, {4, 4}},  // 3 down
      {{2, 1}, {2, 2}, {2, 3}, {2, 4}},          // 4 across
      {{2, 3}, {3, 3}, {4, 3}, {5, 3}},          // 5 down
      {{3, 0}, {4, 0}, {5, 0}},                  // 6 down
      {{3, 2}, {3, 3}, {3, 4}},                  // 7 across
      {{4, 0}, {4, 1}, {4, 2}, {4, 3}, {4, 4}},  // 8 across
  };
  const int S = static_cast<int>(slots.size());
  auto cell_id = [](int r, int c) { return r * 5 + c; };

  // Every open cell takes exactly one letter: one binary per letter.
  std::map<int, std::vector<Lin>> letter;
  for (const auto& slot : slots) {
    for (const auto& rc : slot) {
      int id = cell_id(rc.first, rc.second);
      if (letter.count(id)) continue;
      std::vector<Lin> v;
      Lin sum;
      for (int ch = 0; ch < 26; ++ch) {
        v.push_back(new_var(h, 0, 1));
        sum = sum + v.back();
      }
      // each open cell holds exactly one letter
      add_row(h, sum, 1, 1);
      letter[id] = v;
    }
  }

  // x[s][w] = 1 when word w fills slot s; only words of the slot's length are offered.
  std::vector<std::vector<Lin>> x(S, std::vector<Lin>(W));
  std::vector<std::vector<char>> ok(S, std::vector<char>(W, 0));
  for (int s = 0; s < S; ++s) {
    Lin one;
    for (int w = 0; w < W; ++w) {
      if (words[w].size() != slots[s].size()) continue;
      x[s][w] = new_var(h, 0, 1);
      ok[s][w] = 1;
      one = one + x[s][w];
    }
    // each slot is filled by exactly one word of its length
    add_row(h, one, 1, 1);
  }

  // A word that fills a slot writes its letters into the slot's cells, so crossing cells agree.
  for (int s = 0; s < S; ++s) {
    for (int w = 0; w < W; ++w) {
      if (!ok[s][w]) continue;
      for (size_t p = 0; p < slots[s].size(); ++p) {
        int id = cell_id(slots[s][p].first, slots[s][p].second);
        int ch = words[w][p] - 'A';
        // filling slot s with word w forces the cell to carry the word's letter
        add_row(h, letter[id][ch] - x[s][w], 0, kHighsInf);
      }
    }
  }

  // Each word is used in at most one slot.
  for (int w = 0; w < W; ++w) {
    Lin used;
    for (int s = 0; s < S; ++s)
      if (ok[s][w]) used = used + x[s][w];
    // a word fills at most one slot
    add_row(h, used, 0, 1);
  }

  // E[i] is the word index that fills the slot with puzzle number i+1.
  std::vector<Lin> E(S);
  for (int s = 0; s < S; ++s)
    for (int w = 0; w < W; ++w)
      if (ok[s][w]) E[s] = E[s] + static_cast<double>(w) * x[s][w];

  out.add("E", E);
}
