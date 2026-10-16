// Assign 4 jobs to 3 machines. Each job runs on exactly one machine, each machine
// takes at most 2 jobs, and jobs 0 and 1 are on different machines.
#include <cmath>
#include <cstdio>
#include <vector>

#include "Highs.h"

// Adds a binary column and returns its index.
HighsInt binary(Highs& h) {
  HighsInt k = h.getNumCol();
  h.addVar(0, 1);
  h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

// Adds the row lo <= sum coef * column <= hi.
void row(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& coefs, double lo, double hi) {
  h.addRow(lo, hi, static_cast<HighsInt>(cols.size()), cols.data(), coefs.data());
}

int main() {
  const int jobs = 4, machines = 3;
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});

  // x[j][m] = 1 when job j runs on machine m; the column index is j * machines + m.
  std::vector<HighsInt> x(jobs * machines);
  for (auto& column : x) column = binary(h);
  auto at = [&](int j, int m) { return x[j * machines + m]; };

  for (int j = 0; j < jobs; ++j) {  // one machine per job
    std::vector<HighsInt> cols;
    std::vector<double> coefs;
    for (int m = 0; m < machines; ++m) { cols.push_back(at(j, m)); coefs.push_back(1); }
    row(h, cols, coefs, 1, 1);
  }
  for (int m = 0; m < machines; ++m) {  // at most two jobs per machine
    std::vector<HighsInt> cols;
    std::vector<double> coefs;
    for (int j = 0; j < jobs; ++j) { cols.push_back(at(j, m)); coefs.push_back(1); }
    row(h, cols, coefs, -kHighsInf, 2);
  }
  for (int m = 0; m < machines; ++m)  // jobs 0 and 1 never share a machine
    row(h, {at(0, m), at(1, m)}, {1, 1}, -kHighsInf, 1);

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::printf("no assignment: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  const auto& value = h.getSolution().col_value;
  for (int j = 0; j < jobs; ++j)
    for (int m = 0; m < machines; ++m)
      if (std::lround(value[at(j, m)]) == 1) std::printf("job %d -> machine %d\n", j, m);
  std::printf("status: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
  return 0;
}
