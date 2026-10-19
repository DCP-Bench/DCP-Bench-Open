#include "dcp.h"

// Assign flight attendants to flights. Each flight needs a number of cabin crew
// and certain languages; a crew member who attends a flight has the next two
// flights off.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // attributes[p] = [steward, hostess, French, Spanish, German] for attendant p
  const json& attributes = instance.at("attributes");
  // required_crew[f] = [crew size, stewards, hostesses, French, Spanish, German] for flight f
  const json& required = instance.at("required_crew");
  int people = static_cast<int>(attributes.size());
  int flights = static_cast<int>(required.size());

  // crew[f][p] = 1 if attendant p is assigned to flight f
  std::vector<std::vector<dcp::Lin>> crew(flights);
  for (int f = 0; f < flights; ++f)
    for (int p = 0; p < people; ++p)
      crew[f].push_back(dcp::new_var(h, 0, 1));

  // each flight has exactly the number of cabin crew it needs
  for (int f = 0; f < flights; ++f) {
    dcp::Lin total(0.0);
    for (int p = 0; p < people; ++p) total = total + crew[f][p];
    int size = required[f][0].get<int>();
    dcp::add_row(h, total, size, size);
  }

  // each flight has at least the required number of stewards, hostesses,
  // and French, Spanish and German speakers
  for (int f = 0; f < flights; ++f) {
    for (int k = 0; k < 5; ++k) {
      dcp::Lin count(0.0);
      for (int p = 0; p < people; ++p)
        count = count + attributes[p][k].get<int>() * crew[f][p];
      int need = required[f][k + 1].get<int>();
      dcp::add_row(h, count, need, kHighsInf);
    }
  }

  // after an attended flight, a crew member has the next two flights off
  for (int p = 0; p < people; ++p) {
    for (int f = 0; f < flights; ++f) {
      for (int g = f + 1; g <= f + 2 && g < flights; ++g) {
        dcp::add_row(h, crew[f][p] + crew[g][p], -kHighsInf, 1);
      }
    }
  }

  out.add("crew", crew);
}
