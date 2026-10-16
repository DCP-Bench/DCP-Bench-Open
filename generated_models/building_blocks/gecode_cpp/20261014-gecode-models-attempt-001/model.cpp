#include "dcp.h"

// Alphabet blocks: place every letter of the alphabet on one face of one of the
// blocks, so that each given word can be spelled by arranging the blocks.
// dice[i] is the block that carries letter i of the alphabet.
class BuildingBlocks : public dcp::Space {
 protected:
  IntVarArray dice;  // dice[i]: block carrying the i-th letter of the alphabet

 public:
  explicit BuildingBlocks(const json& instance) {
    int num_blocks = instance.at("num_blocks").get<int>();
    int num_sides = instance.at("num_sides").get<int>();
    std::string alphabet = instance.at("alphabet").get<std::string>();
    std::vector<std::string> words = instance.at("words_str").get<std::vector<std::string>>();
    int num_letters = static_cast<int>(alphabet.size());

    dice = IntVarArray(*this, num_letters, 0, num_blocks - 1);

    // every block has one letter on each of its sides
    for (int b = 0; b < num_blocks; ++b) count(*this, dice, b, IRT_EQ, num_sides);

    // a word is spelled one letter at a time, each from a different block
    for (const auto& word : words) {
      IntVarArgs blocks;
      for (char c : word) {
        std::size_t pos = alphabet.find(c);
        if (pos == std::string::npos) throw std::runtime_error(std::string("letter not in alphabet: ") + c);
        blocks << dice[static_cast<int>(pos)];
      }
      distinct(*this, blocks, IPL_DOM);
    }

    branch(*this, dice, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("dice", dice);
  }

  BuildingBlocks(BuildingBlocks& s) : dcp::Space(s) { dice.update(*this, s.dice); }
  Gecode::Space* copy() override { return new BuildingBlocks(*this); }
};

DCP_MODEL(BuildingBlocks)
