// Job-shop with makespan minimisation. s[j][k] is the start of task k of job j.
// Two tasks on the same machine are ordered by a binary o (big-M = horizon).
#include <cmath>
#include <cstdio>
#include <fstream>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

static HighsInt newInt(Highs& h, double lo, double hi) {
  HighsInt k = h.getNumCol();
  h.addVar(lo, hi);
  h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

struct Task {
  int j, k, d;
};

int main(int argc, char** argv) {
  if (argc < 2) return 1;
  std::ifstream file(argv[1]);
  nlohmann::json data = nlohmann::json::parse(file);
  auto jobs = data.at("jobs").get<std::vector<std::vector<std::vector<int>>>>();
  const int J = static_cast<int>(jobs.size());

  // Horizon: the sum of all durations bounds every start in a left-shifted schedule.
  int H = 0;
  int numMachines = 0;
  for (const auto& job : jobs)
    for (const auto& t : job) {
      H += t[1];
      if (t[0] + 1 > numMachines) numMachines = t[0] + 1;
    }

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);
  h.changeObjectiveSense(ObjSense::kMinimize);

  std::vector<std::vector<HighsInt>> s(J);
  for (int j = 0; j < J; ++j)
    for (size_t k = 0; k < jobs[j].size(); ++k) s[j].push_back(newInt(h, 0, H));
  HighsInt cmax = newInt(h, 0, H);
  h.changeColCost(cmax, 1);

  // Makespan is at least the end of every job.
  for (int j = 0; j < J; ++j) {
    int last = static_cast<int>(jobs[j].size()) - 1;
    HighsInt cols[2] = {cmax, s[j][last]};
    double vals[2] = {1, -1};
    h.addRow(jobs[j][last][1], kHighsInf, 2, cols, vals);
  }

  // Tasks of a job run in order.
  for (int j = 0; j < J; ++j) {
    for (size_t k = 0; k + 1 < jobs[j].size(); ++k) {
      HighsInt cols[2] = {s[j][k + 1], s[j][k]};
      double vals[2] = {1, -1};
      h.addRow(jobs[j][k][1], kHighsInf, 2, cols, vals);
    }
  }

  // A machine runs one task at a time.
  std::vector<std::vector<Task>> on(numMachines);
  for (int j = 0; j < J; ++j)
    for (size_t k = 0; k < jobs[j].size(); ++k)
      on[jobs[j][k][0]].push_back({j, static_cast<int>(k), jobs[j][k][1]});
  for (const auto& tasks : on) {
    for (size_t p = 0; p < tasks.size(); ++p) {
      for (size_t q = p + 1; q < tasks.size(); ++q) {
        const Task& a = tasks[p];
        const Task& b = tasks[q];
        HighsInt o = newInt(h, 0, 1);  // o = 1: a before b; o = 0: b before a
        // o = 1 implies s_a + d_a <= s_b:  s_a - s_b + H o <= H - d_a
        HighsInt c1[3] = {s[a.j][a.k], s[b.j][b.k], o};
        double v1[3] = {1, -1, static_cast<double>(H)};
        h.addRow(-kHighsInf, H - a.d, 3, c1, v1);
        // o = 0 implies s_b + d_b <= s_a:  s_b - s_a - H o <= -d_b
        HighsInt c2[3] = {s[b.j][b.k], s[a.j][a.k], o};
        double v2[3] = {1, -1, -static_cast<double>(H)};
        h.addRow(-kHighsInf, -b.d, 3, c2, v2);
      }
    }
  }

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::fprintf(stderr, "not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }

  const std::vector<double>& val = h.getSolution().col_value;
  std::printf("{\"start\": [");
  for (int j = 0; j < J; ++j) {
    std::printf("%s[", j ? ", " : "");
    for (size_t k = 0; k < jobs[j].size(); ++k)
      std::printf("%s%ld", k ? ", " : "", std::lround(val[s[j][k]]));
    std::printf("]");
  }
  std::printf("]}\n");
  return 0;
}
