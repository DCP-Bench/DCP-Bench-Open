// Building blocks: place each letter of the alphabet on one side of one block so that every word can be spelled.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int num_blocks = instance.at("num_blocks");
  int num_sides = instance.at("num_sides");
  int num_letters = instance.at("num_letters");
  std::string alphabet = instance.at("alphabet").get<std::string>();
  std::vector<std::string> words = instance.at("words_str").get<std::vector<std::string>>();

  // dice[i] is the block that carries the letter alphabet[i]
  vec<IntVar*> dice;
  createVars(dice, num_letters, 0, num_blocks - 1);

  // every block has exactly num_sides letters, one per side
  for (int b = 0; b < num_blocks; ++b) {
    // the letters placed on block b
    vec<BoolView> on_block;
    for (int i = 0; i < num_letters; ++i) {
      BoolView here = newBoolVar();
      int_rel_reif(dice[i], IRT_EQ, b, here);
      on_block.push(here);
    }
    // the number of letters on block b is the number of sides
    bool_linear(on_block, IRT_EQ, getConstant(num_sides));
  }

  // every word is spelled with one block per letter, so the letters of a word lie on different blocks
  for (const std::string& word : words) {
    vec<IntVar*> letter_blocks;
    for (char ch : word) {
      int index = static_cast<int>(alphabet.find(ch));
      letter_blocks.push(dice[index]);
    }
    all_different(letter_blocks);
  }

  // search on the letters in alphabet order
  branch(dice, VAR_INORDER, VAL_MIN);

  json placement = json::array();
  for (int i = 0; i < num_letters; ++i) placement.push_back(dcp::out(dice[i]));
  outputs = {{"dice", placement}};
}
