// Crossword: choose 8 different words from a list of 15 so that the grid can be filled,
// the numbered squares being the starts of the words.
#include "dcp.h"

#include <string>

void Build(const json& instance, json& outputs) {
  // The word list is part of the problem statement, sorted by length (longest first)
  // and then alphabetically, which is the numbering used for the output.
  const std::vector<std::string> words = {
      "HOSES", "LASER", "SAILS", "SHEET", "STEER", "HEEL", "HIKE", "KEEL",
      "KNOT",  "LINE",  "AFT",   "ALE",   "EEL",   "LEE",  "TIE"};
  const int W = static_cast<int>(words.size());

  // E[k] is the index of the word that starts at square k+1 of the puzzle
  vec<IntVar*> E;
  createVars(E, 8, 0, W - 1, true);

  // The grid has 6 rows and 5 columns. letter[r][c] is the letter in a free cell, coded 'A'..'Z';
  // a cell is created the first time a word slot covers it.
  std::vector<std::vector<IntVar*>> letter(6, std::vector<IntVar*>(5, nullptr));
  auto cell = [&](int r, int c) -> IntVar* {
    if (letter[r][c] == nullptr) letter[r][c] = newIntVar('A', 'Z');
    return letter[r][c];
  };

  // The words of the puzzle: slot k starts at (row, col), runs across or down, with a length.
  struct Slot { int r, c; bool across; int len; };
  const Slot slots[8] = {
      {0, 0, true, 5},   // 1 across
      {0, 2, false, 5},  // 2 down
      {0, 4, false, 5},  // 3 down
      {2, 1, true, 4},   // 4 across
      {2, 3, false, 4},  // 5 down
      {3, 0, false, 3},  // 6 down
      {3, 2, true, 3},   // 7 across
      {4, 0, true, 5},   // 8 across
  };

  // Each slot holds the selected word: slot letters and the word index go together,
  // so the word must have the slot's length and spell the letters in the grid cells.
  for (int k = 0; k < 8; ++k) {
    vec<IntVar*> vars;
    vars.push(E[k]);
    for (int i = 0; i < slots[k].len; ++i) {
      int r = slots[k].r + (slots[k].across ? 0 : i);
      int c = slots[k].c + (slots[k].across ? i : 0);
      vars.push(cell(r, c));
    }
    vec<vec<int>> tuples;
    for (int w = 0; w < W; ++w) {
      if (static_cast<int>(words[w].size()) != slots[k].len) continue;
      vec<int> t;
      t.push(w);
      for (char ch : words[w]) t.push(ch);
      tuples.push();
      for (int i = 0; i < t.size(); ++i) tuples.last().push(t[i]);
    }
    table(vars, tuples);
  }

  // we select 8 words from the list, so each word is used at most once
  all_different(E);

  branch(E, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int k = 0; k < 8; ++k) arr.push_back(dcp::out(E[k]));
  outputs = {{"E", arr}};
}
