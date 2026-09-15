#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Movie scheduling: watch as many films as possible without two of them
// overlapping in time.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // Each movie row is title, start, end, so the row mixes a string with two
  // integers and the times are read positionally.
  const json& movies = instance.at("movies");
  const int num_movies = static_cast<int>(movies.size());

  std::vector<int64_t> start;
  std::vector<int64_t> end;
  for (int i = 0; i < num_movies; ++i) {
    start.push_back(movies.at(i).at(1).get<int64_t>());
    end.push_back(movies.at(i).at(2).get<int64_t>());
  }

  std::vector<BoolVar> selected_movies;
  for (int i = 0; i < num_movies; ++i) {
    selected_movies.push_back(model.NewBoolVar());
  }

  for (int i = 0; i < num_movies; ++i) {
    for (int j = 0; j < num_movies; ++j) {
      if (i == j) continue;
      if (end[i] > start[j] && end[j] > start[i]) {
        model.AddLessOrEqual(selected_movies[i] + selected_movies[j], 1);
      }
    }
  }

  LinearExpr watched;
  for (int i = 0; i < num_movies; ++i) watched += selected_movies[i];
  model.Maximize(watched);

  json out = json::array();
  for (const BoolVar& b : selected_movies) out.push_back(b.index());
  outputs = {{"selected_movies", out}};
}
