#include <algorithm>
#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Packing rectangles: place rectangular items (given widths and heights)
// inside one larger rectangle without overlap, so that the area of the larger
// rectangle is as small as possible. Positions start from 0.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> widths = instance.at("widths").get<std::vector<int64_t>>();
  const std::vector<int64_t> heights = instance.at("heights").get<std::vector<int64_t>>();
  const int n = static_cast<int>(widths.size());

  // The enclosing rectangle is at least as wide as the widest item and at
  // most as wide as all items side by side; the same holds for the height.
  const int64_t area_min_x = *std::max_element(widths.begin(), widths.end());
  const int64_t area_max_x = std::accumulate(widths.begin(), widths.end(), int64_t{0});
  const int64_t area_min_y = *std::max_element(heights.begin(), heights.end());
  const int64_t area_max_y = std::accumulate(heights.begin(), heights.end(), int64_t{0});

  // pos_x[i], pos_y[i] is the position of item i (its lower-left corner).
  std::vector<IntVar> pos_x, pos_y;
  for (int i = 0; i < n; ++i) {
    pos_x.push_back(model.NewIntVar(Domain(0, area_max_x)));
    pos_y.push_back(model.NewIntVar(Domain(0, area_max_y)));
  }
  // Width and height of the enclosing rectangle.
  const IntVar total_x = model.NewIntVar(Domain(area_min_x, area_max_x));
  const IntVar total_y = model.NewIntVar(Domain(area_min_y, area_max_y));

  // Every item has to be within the overall area.
  for (int i = 0; i < n; ++i) {
    model.AddLessOrEqual(pos_x[i] + widths[i], total_x);
    model.AddLessOrEqual(pos_y[i] + heights[i], total_y);
  }

  // No overlap: every item has to be fully left of, right of, above or below
  // every other item. The reference states this as a disjunction for each
  // pair of items; the two-dimensional no-overlap constraint says the same
  // thing for the rectangles made of the x and y intervals of every item.
  NoOverlap2DConstraint no_overlap = model.AddNoOverlap2D();
  for (int i = 0; i < n; ++i) {
    const IntervalVar x_interval = model.NewFixedSizeIntervalVar(pos_x[i], widths[i]);
    const IntervalVar y_interval = model.NewFixedSizeIntervalVar(pos_y[i], heights[i]);
    no_overlap.AddRectangle(x_interval, y_interval);
  }

  // Minimize the area of the enclosing rectangle, total_x * total_y.
  const IntVar area = model.NewIntVar(Domain(area_min_x * area_min_y, area_max_x * area_max_y));
  model.AddMultiplicationEquality(area, {total_x, total_y});
  model.Minimize(area);

  json px = json::array(), py = json::array();
  for (const IntVar& v : pos_x) px.push_back(v.index());
  for (const IntVar& v : pos_y) py.push_back(v.index());
  outputs = {{"pos_x", px}, {"pos_y", py}, {"total_x", total_x.index()}, {"total_y", total_y.index()}};
}
