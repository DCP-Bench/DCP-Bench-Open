// Crossword: complete the puzzle grid (6 rows, 5 columns, '#' cells are blocks) by
// selecting 8 of the 15 listed words, one per word slot, so that crossing letters agree.
// Output E: the 8 selected word indices, starting from 0, in ascending order.
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
  const int K = 8;  // words to select

  // The word slots of the grid, as (row, column) cells, 0-based: the 4 across and 4 down
  // runs of open cells of length 2 or more, numbered 1..8 in the puzzle.
  const std::vector<std::vector<std::pair<int, int>>> slots = {
      {{0, 0}, {0, 1}, {0, 2}, {0, 3}, {0, 4}},  // across 1
      {{2, 1}, {2, 2}, {2, 3}, {2, 4}},          // across 4
      {{3, 2}, {3, 3}, {3, 4}},                  // across 7
      {{4, 0}, {4, 1}, {4, 2}, {4, 3}, {4, 4}},  // across 8
      {{3, 0}, {4, 0}, {5, 0}},                  // down 6
      {{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 2}},  // down 2
      {{0, 4}, {1, 4}, {2, 4}, {3, 4}, {4, 4}},  // down 3
      {{2, 3}, {3, 3}, {4, 3}, {5, 3}},          // down 5
  };
  const int S = static_cast<int>(slots.size());
  auto cell_id = [](int r, int c) { return r * 5 + c; };

  // Every open cell of a slot takes exactly one letter: one binary per letter.
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

  // z[k][w] = 1 when the k-th selected word (in ascending order) is word w.
  std::vector<std::vector<Lin>> z(K, std::vector<Lin>(W));
  for (int k = 0; k < K; ++k) {
    Lin one;
    for (int w = 0; w < W; ++w) {
      z[k][w] = new_var(h, 0, 1);
      one = one + z[k][w];
    }
    // each position of the selected list holds exactly one word
    add_row(h, one, 1, 1);
  }

  // Each word is used at most once, and the selected words are the words in the slots.
  for (int w = 0; w < W; ++w) {
    Lin in_slots, in_list;
    for (int s = 0; s < S; ++s)
      if (ok[s][w]) in_slots = in_slots + x[s][w];
    for (int k = 0; k < K; ++k) in_list = in_list + z[k][w];
    // a word in the list is exactly a word in a slot
    add_row(h, in_slots - in_list, 0, 0);
    // a word fills at most one slot
    add_row(h, in_slots, 0, 1);
  }

  // The selected list E: E[k] is the index of the k-th selected word.
  std::vector<Lin> E(K);
  for (int k = 0; k < K; ++k)
    for (int w = 0; w < W; ++w) E[k] = E[k] + static_cast<double>(w) * z[k][w];

  // the selected words are listed in ascending order, so no word repeats
  for (int k = 0; k + 1 < K; ++k) add_row(h, E[k + 1] - E[k], 1, kHighsInf);

  out.add("E", E);
}
