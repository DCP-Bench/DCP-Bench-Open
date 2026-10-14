// Crew assignment: assign cabin crew to flights so that each flight is staffed and
// every crew member gets two flights off after each flight they work.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // attributes[p][0] = 1 if person p is a steward, attributes[p][1] = 1 if a hostess,
  // attributes[p][2..4] = 1 if p speaks the language of category 2..4 (see required_crew)
  std::vector<std::vector<int>> attributes = instance.at("attributes").get<std::vector<std::vector<int>>>();
  // required_crew[f][0] = total crew on flight f; required_crew[f][1..5] = minimum number of
  // people of category 0..4 (steward, hostess, three languages) on flight f
  std::vector<std::vector<int>> required = instance.at("required_crew").get<std::vector<std::vector<int>>>();
  int np = static_cast<int>(attributes.size());   // number of crew members
  int nf = static_cast<int>(required.size());     // number of flights
  int nc = static_cast<int>(attributes[0].size()); // number of attribute categories (5)

  // crew[f][p] = 1 if person p is assigned to flight f
  vec<vec<IntVar*>> crew;
  createVars(crew, nf, np, 0, 1, true);

  // every flight has exactly the required total number of crew members
  for (int f = 0; f < nf; ++f) {
    // the number of people assigned to flight f is its total crew requirement
    vec<IntVar*> on;
    for (int p = 0; p < np; ++p) on.push(crew[f][p]);
    int_linear(on, IRT_EQ, required[f][0]);
  }

  // every flight has enough stewards, hostesses and speakers of each language
  for (int f = 0; f < nf; ++f) {
    for (int k = 0; k < nc; ++k) {
      // the people on flight f in category k must reach the required minimum
      vec<int> coef;
      vec<IntVar*> on;
      for (int p = 0; p < np; ++p) {
        coef.push(attributes[p][k]);
        on.push(crew[f][p]);
      }
      int_linear(coef, on, IRT_GE, required[f][1 + k]);
    }
  }

  // after working a flight, a crew member has the next two flights off:
  // at most one of flights f, f+1, f+2 can be worked by the same person
  for (int p = 0; p < np; ++p) {
    for (int f = 0; f < nf; ++f) {
      for (int d = 1; d <= 2 && f + d < nf; ++d) {
        // a person who works flight f does not work flight f+d
        bin_linear(crew[f][p], crew[f + d][p], IRT_LE, 1);
      }
    }
  }

  // search over the assignment flight by flight
  vec<IntVar*> flat;
  flatten(crew, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int f = 0; f < nf; ++f) {
    json row = json::array();
    for (int p = 0; p < np; ++p) row.push_back(dcp::out(crew[f][p]));
    rows.push_back(row);
  }
  outputs = {{"crew", rows}};
}
