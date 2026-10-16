// Addition cryptarithm. One binary y[l][v] per letter l and digit v; the digit is sum_v v y[l][v].
#include <cstdio>
#include <fstream>
#include <map>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

static HighsInt newBin(Highs& h) {
  HighsInt k = h.getNumCol();
  h.addVar(0, 1);
  h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

int main(int argc, char** argv) {
  if (argc < 2) return 1;
  std::ifstream file(argv[1]);
  nlohmann::json data = nlohmann::json::parse(file);
  std::vector<std::string> addends = data.at("addends").get<std::vector<std::string>>();
  std::string sum = data.at("sum").get<std::string>();

  // coef[c] = (place values in the addends) - (place values in the sum)
  std::map<char, double> coef;
  std::map<char, bool> leading;
  auto addWord = [&](const std::string& w, double sign) {
    double place = 1;
    for (int k = static_cast<int>(w.size()) - 1; k >= 0; --k) {
      coef[w[k]] += sign * place;
      place *= 10;
    }
    if (w.size() > 1) leading[w[0]] = true;
  };
  for (const auto& w : addends) addWord(w, 1);
  addWord(sum, -1);

  std::vector<char> letters;
  for (const auto& kv : coef) letters.push_back(kv.first);
  const int L = static_cast<int>(letters.size());

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);

  // Column l * 10 + v is "letter l takes digit v". A leading letter cannot take 0.
  for (int l = 0; l < L; ++l) {
    bool nonzero = leading.count(letters[l]) > 0;
    for (int v = 0; v < 10; ++v) {
      HighsInt k = newBin(h);
      if (v == 0 && nonzero) h.changeColBounds(k, 0, 0);
    }
  }

  // Each letter has exactly one digit.
  for (int l = 0; l < L; ++l) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int v = 0; v < 10; ++v) { cols.push_back(l * 10 + v); ones.push_back(1); }
    h.addRow(1, 1, 10, cols.data(), ones.data());
  }

  // Different letters get different digits.
  for (int v = 0; v < 10; ++v) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int l = 0; l < L; ++l) { cols.push_back(l * 10 + v); ones.push_back(1); }
    h.addRow(-kHighsInf, 1, L, cols.data(), ones.data());
  }

  // Sum over addends minus the sum word is zero.
  {
    std::vector<HighsInt> cols;
    std::vector<double> vals;
    for (int l = 0; l < L; ++l) {
      for (int v = 0; v < 10; ++v) {
        cols.push_back(l * 10 + v);
        vals.push_back(coef[letters[l]] * v);
      }
    }
    h.addRow(0, 0, static_cast<HighsInt>(cols.size()), cols.data(), vals.data());
  }

  h.run();
  if (h.getModelStatus() == HighsModelStatus::kInfeasible) {
    std::printf("{\"status\": \"unsatisfiable\"}\n");
    return 0;
  }
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::fprintf(stderr, "not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }

  const std::vector<double>& val = h.getSolution().col_value;
  std::printf("{\"digits\": {");
  for (int l = 0; l < L; ++l) {
    int digit = 0;
    double best = -1;
    for (int v = 0; v < 10; ++v) {
      if (val[l * 10 + v] > best) { best = val[l * 10 + v]; digit = v; }
    }
    std::printf("%s\"%c\": %d", l ? ", " : "", letters[l], digit);
  }
  std::printf("}}\n");
  return 0;
}
