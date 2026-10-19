// Media selection: choose which advertising media to buy so that every target audience
// is reached by at least one selected medium, at minimum total campaign cost.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& incidence = instance.at("incidence_matrix");  // incidence[audience][medium] = 1 if the medium reaches the audience
  const auto& costs = instance.at("media_costs");
  const int num_audiences = static_cast<int>(instance.at("target_audiences").size());
  const int num_media = static_cast<int>(instance.at("advertising_media").size());

  // is_selected[m] = 1 if medium m is selected for the campaign
  std::vector<dcp::Lin> is_selected;
  for (int m = 0; m < num_media; ++m) is_selected.push_back(dcp::new_var(h, 0, 1));

  // every target audience is reached by at least one selected medium
  for (int a = 0; a < num_audiences; ++a) {
    dcp::Lin reached;
    for (int m = 0; m < num_media; ++m) {
      int covers = incidence.at(a).at(m).get<int>();
      if (covers != 0) reached = reached + covers * is_selected[m];
    }
    dcp::add_row(h, reached, 1, kHighsInf);
  }

  // total campaign cost: the sum of the costs of the selected media
  dcp::Lin total_cost;
  for (int m = 0; m < num_media; ++m) {
    total_cost = total_cost + costs.at(m).get<int>() * is_selected[m];
  }

  // minimise the total campaign cost
  out.minimize(total_cost);

  out.add("is_selected", is_selected);
  out.add("min_total_cost", total_cost);
}
