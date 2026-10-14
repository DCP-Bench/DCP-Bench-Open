// Movie scheduling: choose the largest set of films whose filming periods do not overlap (interval scheduling).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // each movie is [title, first day, last day]
  const json& movies = instance.at("movies");
  int num_movies = static_cast<int>(movies.size());

  // selected[i] = 1 if movie i is accepted
  vec<IntVar*> selected;
  createVars(selected, num_movies, 0, 1, true);

  // two movies conflict when their filming periods share a day
  for (int i = 0; i < num_movies; ++i) {
    int first_i = movies[i][1].get<int>();
    int last_i = movies[i][2].get<int>();
    for (int j = i + 1; j < num_movies; ++j) {
      int first_j = movies[j][1].get<int>();
      int last_j = movies[j][2].get<int>();
      if (first_i <= last_j && first_j <= last_i) {
        // the two movies overlap, so at most one of them can be accepted
        vec<IntVar*> pair;
        pair.push(selected[i]);
        pair.push(selected[j]);
        int_linear(pair, IRT_LE, 1);
      }
    }
  }

  // the number of accepted movies is the number of selected movies
  vec<int> ones;
  for (int i = 0; i < num_movies; ++i) ones.push(1);
  IntVar* count = newIntVar(0, num_movies);
  int_linear(ones, selected, IRT_EQ, count);

  // search on the movies in list order
  branch(selected, VAR_INORDER, VAL_MAX);

  // maximize the number of movies accepted
  optimize(count, OPT_MAX);

  json picks = json::array();
  for (int i = 0; i < num_movies; ++i) picks.push_back(dcp::out(selected[i]));
  outputs = {{"selected_movies", picks}};
}
