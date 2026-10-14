// General store puzzle (SEND-MORE-style cryptarithm): find the digit of each letter so that the sum of the
// words above the line equals ALL WOOL, with each different letter standing for a different digit.
#include <string>
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the letters of the puzzle, in a fixed order; L[k] is the digit of letters[k]
  const std::string letters = "ABCEHLOPSW";
  int nl = static_cast<int>(letters.size());

  vec<IntVar*> L;
  createVars(L, nl, 0, 9, true);

  // each different letter stands for a different digit
  all_different(L);

  // the addends, one per line of the sum, and the total
  const std::vector<std::string> addends = {"CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE",
                                            "COOL", "BASS", "HOPS", "ALES", "HOES", "APPLES",
                                            "COWS", "CHEESE", "CHSOAP", "SHEEP"};
  const std::string total = "ALLWOOL";

  // weight[k] = sum of place values of letters[k] in the addends minus in the total
  // place values: the letter at position p (from the left) of a word of length len has value 10^(len-1-p)
  std::vector<long long> weight(nl, 0);
  for (const std::string& word : addends) {
    int len = static_cast<int>(word.size());
    long long place = 1;
    for (int p = len - 1; p >= 0; --p) {
      weight[letters.find(word[p])] += place;
      place *= 10;
    }
  }
  {
    int len = static_cast<int>(total.size());
    long long place = 1;
    for (int p = len - 1; p >= 0; --p) {
      weight[letters.find(total[p])] -= place;
      place *= 10;
    }
  }

  // the sum of the addends, each letter weighted by its place value, equals the total
  vec<int> coef;
  for (int k = 0; k < nl; ++k) coef.push(static_cast<int>(weight[k]));
  int_linear(coef, L, IRT_EQ, 0);

  branch(L, VAR_INORDER, VAL_MIN);

  json values = json::object();
  for (int k = 0; k < nl; ++k) values[std::string(1, letters[k])] = dcp::out(L[k]);
  outputs = values;
}
