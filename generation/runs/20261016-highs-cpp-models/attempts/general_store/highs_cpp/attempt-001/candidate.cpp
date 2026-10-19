// General store puzzle: the sum of the sixteen words CHESS, CASH, BOWWOW, CHOPS, ALSOPS,
// PALEALE, COOL, BASS, HOPS, ALES, HOES, APPLES, COWS, CHEESE, CHSOAP, SHEEP equals ALLWOOL.
// Each different letter stands for a different digit (0 to 9). Find the digit of each letter.
// The problem has no instance data: the words are fixed by the description.
#include "dcp.h"

#include <string>
#include <vector>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;
  // The ten letters of the puzzle, in output order.
  const std::string letters = "ABCEHLOPSW";
  const int count = static_cast<int>(letters.size());

  // y[l][d] = 1 when letter l stands for digit d.
  std::vector<std::vector<dcp::Lin>> y(count, std::vector<dcp::Lin>(10));
  for (int l = 0; l < count; ++l)
    for (int d = 0; d < 10; ++d) y[l][d] = dcp::new_var(h, 0, 1);

  // digit[l] is the digit of letter l.
  std::vector<dcp::Lin> digit(count);
  for (int l = 0; l < count; ++l) {
    digit[l] = dcp::new_var(h, 0, 9);

    // each letter stands for exactly one digit
    dcp::Lin one_digit;
    for (int d = 0; d < 10; ++d) one_digit = one_digit + y[l][d];
    dcp::add_row(h, one_digit, 1, 1);

    // the digit of the letter is the digit its indicator selects
    dcp::Lin value;
    for (int d = 0; d < 10; ++d) value = value + static_cast<double>(d) * y[l][d];
    dcp::add_row(h, digit[l] - value, 0, 0);
  }

  // each different letter stands for a different digit: ten letters and ten digits,
  // so every digit is used by exactly one letter
  for (int d = 0; d < 10; ++d) {
    dcp::Lin used;
    for (int l = 0; l < count; ++l) used = used + y[l][d];
    dcp::add_row(h, used, 1, 1);
  }

  // the words above the line add up to ALLWOOL. A word's value is the sum of its
  // letters' digits times their place values, so each letter gets a coefficient
  // (its place values summed over all words, the total counted negatively).
  std::vector<double> coef(count, 0.0);
  auto add_word = [&](const std::string& word, double sign) {
    double place = 1.0;
    for (int i = static_cast<int>(word.size()) - 1; i >= 0; --i) {
      coef[letters.find(word[i])] += sign * place;
      place *= 10.0;
    }
  };
  const std::vector<std::string> addends = {
      "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
      "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"};
  for (const auto& word : addends) add_word(word, 1.0);
  add_word("ALLWOOL", -1.0);

  // the sum of the words above the line equals the total ALLWOOL
  dcp::Lin sum;
  for (int l = 0; l < count; ++l) sum = sum + coef[l] * digit[l];
  dcp::add_row(h, sum, 0, 0);

  // the outputs are the digit of each letter
  for (int l = 0; l < count; ++l) out.add(std::string(1, letters[l]), digit[l]);
}
