#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Crossword: choose a different word from a list of 15 for each of the 8
// numbered slots of a fixed 5 x 6 grid so that crossing slots share the same
// letter where they cross.
// The problem has no instance data: the word list, the grid and its crossings
// are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // Words sorted longest first, then alphabetically (the numbering the
  // output uses). Letters are coded a = 1 .. z = 26; positions past the end
  // of a short word hold 0.
  const std::vector<std::string> words = {"HOSES", "LASER", "SAILS", "SHEET", "STEER",
                                          "HEEL",  "HIKE",  "KEEL",  "KNOT",  "LINE",
                                          "AFT",   "ALE",   "EEL",   "LEE",   "TIE"};
  const int word_len = 5;
  const int num_words = static_cast<int>(words.size());
  // letter[p][w]: code of the letter at position p of word w.
  std::vector<std::vector<int64_t>> letter(word_len, std::vector<int64_t>(num_words, 0));
  for (int w = 0; w < num_words; ++w)
    for (int p = 0; p < static_cast<int>(words[w].size()); ++p)
      letter[p][w] = words[w][p] - 'A' + 1;

  // Crossings {slot1, pos1, slot2, pos2}: letter pos1 of slot1 equals
  // letter pos2 of slot2 (0-based slots and positions).
  const std::vector<std::vector<int>> overlapping = {
      {0, 2, 1, 0}, {0, 4, 2, 0},                              // slot 1 across
      {3, 1, 1, 2}, {3, 2, 4, 0}, {3, 3, 2, 2},                // slot 4 across
      {6, 0, 1, 3}, {6, 1, 4, 1}, {6, 2, 2, 3},                // slot 7 across
      {7, 0, 5, 1}, {7, 2, 1, 4}, {7, 3, 4, 2}, {7, 4, 2, 4},  // slot 8 across
  };

  // E[s]: index of the word placed in slot s. Every slot takes part in a
  // crossing, where the word index selects from the list, so it ranges over
  // the 15 words.
  const int n_slots = 8;
  std::vector<IntVar> E;
  for (int s = 0; s < n_slots; ++s) E.push_back(model.NewIntVar(Domain(0, num_words - 1)));

  // Each word is used at most once.
  model.AddAllDifferent(E);

  // At every crossing the two slots show the same letter.
  for (const std::vector<int>& o : overlapping) {
    const IntVar shared = model.NewIntVar(Domain(0, 26));
    model.AddElement(E[o[0]], letter[o[1]], shared);
    model.AddElement(E[o[2]], letter[o[3]], shared);
  }

  json out = json::array();
  for (const IntVar& v : E) out.push_back(v.index());
  outputs = {{"E", out}};
}
