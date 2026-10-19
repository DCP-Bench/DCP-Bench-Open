// Building blocks: place each letter of the alphabet on one side of one block, so that
// every block carries num_sides letters and every word can be spelled with its letters
// on different blocks. Output dice[l] is the block (0-based) of letter l.
#include "dcp.h"

#include <set>
#include <stdexcept>
#include <string>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int num_blocks = instance.at("num_blocks").get<int>();
  const int num_sides = instance.at("num_sides").get<int>();
  const int num_letters = instance.at("num_letters").get<int>();
  const std::string alphabet = instance.at("alphabet").get<std::string>();
  const json& words = instance.at("words_str");

  // Letter k of the alphabet string is letter number k.
  // on[l][b] is 1 when letter l is on block b.
  std::vector<std::vector<dcp::Lin>> on(num_letters, std::vector<dcp::Lin>(num_blocks));
  for (int l = 0; l < num_letters; ++l)
    for (int b = 0; b < num_blocks; ++b) on[l][b] = dcp::new_var(h, 0, 1);

  // each letter is on exactly one block
  for (int l = 0; l < num_letters; ++l) {
    dcp::Lin one_block;
    for (int b = 0; b < num_blocks; ++b) one_block = one_block + on[l][b];
    dcp::add_row(h, one_block, 1, 1);
  }

  // each block has num_sides letters on its sides
  for (int b = 0; b < num_blocks; ++b) {
    dcp::Lin letters_on_block;
    for (int l = 0; l < num_letters; ++l) letters_on_block = letters_on_block + on[l][b];
    dcp::add_row(h, letters_on_block, num_sides, num_sides);
  }

  // the letters of each word are on distinct blocks, so each block serves at most one of them
  for (const auto& w : words) {
    std::set<int> letters;
    for (char c : w.get<std::string>()) {
      std::size_t pos = alphabet.find(c);
      if (pos == std::string::npos) throw std::runtime_error("word letter not in alphabet");
      letters.insert(static_cast<int>(pos));
    }
    for (int b = 0; b < num_blocks; ++b) {
      dcp::Lin on_block;
      for (int l : letters) on_block = on_block + on[l][b];
      dcp::add_row(h, on_block, -kHighsInf, 1);
    }
  }

  // output: the block of each letter, 0-based
  std::vector<dcp::Lin> dice(num_letters);
  for (int l = 0; l < num_letters; ++l)
    for (int b = 0; b < num_blocks; ++b) dice[l] = dice[l] + static_cast<double>(b) * on[l][b];
  out.add("dice", dice);
}
