// Movie scheduling: an actor is offered n movie projects, each with a first and last
// day of filming. Accepting a movie means being available for its whole interval, so
// two accepted movies may not overlap. Choose the largest set of pairwise
// non-overlapping movies. Output selected_movies[i] is 1 when movie i is selected.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& movies = instance.at("movies");
  int n = static_cast<int>(movies.size());

  // one binary per movie: 1 when the movie is selected
  std::vector<dcp::Lin> sel;
  for (int i = 0; i < n; i++) sel.push_back(dcp::new_var(h, 0, 1));

  // each movie has a first day and a last day of filming, read from the instance
  std::vector<int> first(n), last(n);
  int min_day = 0, max_day = 0;
  for (int i = 0; i < n; i++) {
    first[i] = movies[i][1].get<int>();
    last[i] = movies[i][2].get<int>();
    if (i == 0 || first[i] < min_day) min_day = first[i];
    if (i == 0 || last[i] > max_day) max_day = last[i];
  }

  // two movies overlap when they share a filming day, so on every day at most one
  // selected movie is filming (this covers each overlapping pair)
  for (int d = min_day; d <= max_day; d++) {
    dcp::Lin on_day = 0;
    bool any = false;
    for (int i = 0; i < n; i++) {
      if (first[i] <= d && d <= last[i]) {
        on_day = on_day + sel[i];
        any = true;
      }
    }
    if (any) dcp::add_row(h, on_day, -kHighsInf, 1);
  }

  // the objective counts the selected movies, since every film pays the same fee
  dcp::Lin count = 0;
  for (int i = 0; i < n; i++) count = count + sel[i];
  out.maximize(count);

  out.add("selected_movies", sel);
}
