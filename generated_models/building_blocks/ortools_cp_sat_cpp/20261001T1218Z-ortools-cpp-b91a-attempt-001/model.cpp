#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Building blocks: decide which letters go on which alphabet block so that
// every word in the list can be spelled by taking one letter from each of
// several different blocks, with every block carrying the same number of letters.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_blocks = instance.at("num_blocks").get<int>();
  const int num_sides = instance.at("num_sides").get<int>();
  const int num_letters = instance.at("num_letters").get<int>();
  const std::string alphabet = instance.at("alphabet").get<std::string>();
  const std::vector<std::string> words_str =
      instance.at("words_str").get<std::vector<std::string>>();

  // Letter of the alphabet -> its position, which is the index into dice.
  auto letter_index = [&](char c) {
    return static_cast<int>(alphabet.find(c));
  };

  // dice[l] is the block (0..num_blocks-1) that letter l is placed on.
  // on_block[l][b] is true exactly when dice[l] == b; it is the 0/1 form of
  // dice[l], which keeps the per-block letter count linear.
  std::vector<IntVar> dice;
  std::vector<std::vector<BoolVar>> on_block(num_letters);
  for (int l = 0; l < num_letters; ++l) {
    dice.push_back(model.NewIntVar(Domain(0, num_blocks - 1)));
    LinearExpr one_block;
    LinearExpr block_index;
    for (int b = 0; b < num_blocks; ++b) {
      on_block[l].push_back(model.NewBoolVar());
      one_block += on_block[l][b];
      block_index += b * on_block[l][b];
    }
    model.AddEquality(one_block, 1);
    model.AddEquality(dice[l], block_index);
  }

  // The letters of a word must all be on different blocks.
  for (const std::string& word : words_str) {
    std::vector<IntVar> letters_of_word;
    for (const char c : word) letters_of_word.push_back(dice[letter_index(c)]);
    model.AddAllDifferent(letters_of_word);
  }

  // Each block carries exactly num_sides letters.
  for (int b = 0; b < num_blocks; ++b) {
    LinearExpr letters_on_block;
    for (int l = 0; l < num_letters; ++l) letters_on_block += on_block[l][b];
    model.AddEquality(letters_on_block, num_sides);
  }

  json dice_out = json::array();
  for (const IntVar& d : dice) dice_out.push_back(d.index());
  outputs = {{"dice", dice_out}};
}
