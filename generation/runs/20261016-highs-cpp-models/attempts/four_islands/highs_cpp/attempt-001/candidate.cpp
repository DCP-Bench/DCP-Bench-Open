// Four islands (Pwana, Quero, Rayou, Skern) on a 2x2 map A B / C D: find the primary
// export and tourist attraction of each island, and the map position of each one.
// Positions: A=0 (north-west), B=1 (north-east), C=2 (south-west), D=3 (south-east).
#include "dcp.h"

namespace {

// y[item][p] = 1 when the item sits at map position p. Each item has one position and
// each position holds one item, so each category is a permutation of the four positions.
using Grid = std::vector<std::vector<dcp::Lin>>;

Grid place(Highs& h, int items) {
  Grid y(items, std::vector<dcp::Lin>(4));
  for (int k = 0; k < items; ++k)
    for (int p = 0; p < 4; ++p) y[k][p] = dcp::new_var(h, 0, 1);

  // each item is at exactly one position
  for (int k = 0; k < items; ++k) {
    dcp::Lin one;
    for (int p = 0; p < 4; ++p) one = one + y[k][p];
    dcp::add_row(h, one, 1, 1);
  }
  // each position holds exactly one item
  for (int p = 0; p < 4; ++p) {
    dcp::Lin one;
    for (int k = 0; k < items; ++k) one = one + y[k][p];
    dcp::add_row(h, one, 1, 1);
  }
  return y;
}

// The map position of an item, A=0 .. D=3.
dcp::Lin position(const std::vector<dcp::Lin>& r) {
  dcp::Lin e;
  for (int p = 0; p < 4; ++p) e = e + static_cast<double>(p) * r[p];
  return e;
}

// Row of an item: 0 for the north row (A, B), 1 for the south row (C, D).
dcp::Lin row(const std::vector<dcp::Lin>& r) {
  dcp::Lin e;
  for (int p = 0; p < 4; ++p) e = e + static_cast<double>(p / 2) * r[p];
  return e;
}

// Column of an item: 0 for the west column (A, C), 1 for the east column (B, D).
dcp::Lin col(const std::vector<dcp::Lin>& r) {
  dcp::Lin e;
  for (int p = 0; p < 4; ++p) e = e + static_cast<double>(p % 2) * r[p];
  return e;
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the statement fixes every size: four islands, four exports, four attractions

  // Islands, exports and attractions are listed in the order of the brief's output lists.
  Grid island = place(h, 4);      // Pwana, Quero, Rayou, Skern
  Grid exports = place(h, 4);     // alabaster, bananas, coconuts, durian fruit
  Grid attraction = place(h, 4);  // resort hotel, ice skating rink, jai alai stadium, koala preserve

  const auto& pwana = island[0];
  const auto& quero = island[1];
  const auto& rayou = island[2];
  const auto& skern = island[3];
  const auto& alabaster = exports[0];
  const auto& bananas = exports[1];
  const auto& durian = exports[3];
  const auto& hotel = attraction[0];
  const auto& rink = attraction[1];
  const auto& jai_alai = attraction[2];
  const auto& koala = attraction[3];

  // 1. The island with the koala preserve is due south of Pwana: one row further south, same column.
  dcp::add_row(h, row(koala) - row(pwana), 1, 1);
  dcp::add_row(h, col(koala) - col(pwana), 0, 0);

  // 2. The island with the alabaster quarry is due west of Quero: same row, one column further west.
  dcp::add_row(h, row(alabaster) - row(quero), 0, 0);
  dcp::add_row(h, col(alabaster) - col(quero), -1, -1);

  // 3. The island with the resort hotel is due east of the island exporting durian fruit: same row, one column further east.
  dcp::add_row(h, row(hotel) - row(durian), 0, 0);
  dcp::add_row(h, col(hotel) - col(durian), 1, 1);

  // 4. Skern and the island with the jai alai stadium are connected by a north-south bridge:
  //    same column, and one is in the north row while the other is in the south row.
  dcp::add_row(h, col(skern) - col(jai_alai), 0, 0);
  dcp::add_row(h, row(skern) + row(jai_alai), 1, 1);

  // 5. Rayou and the island exporting bananas are connected by an east-west bridge:
  //    same row, and one is in the west column while the other is in the east column.
  dcp::add_row(h, row(rayou) - row(bananas), 0, 0);
  dcp::add_row(h, col(rayou) + col(bananas), 1, 1);

  // 6. The island with the ice skating rink and the island with the jai alai stadium are not
  //    connected by a bridge: they are diagonal, so they differ in row and in column.
  dcp::add_row(h, row(rink) + row(jai_alai), 1, 1);
  dcp::add_row(h, col(rink) + col(jai_alai), 1, 1);

  // Outputs: map position of each island, export and attraction.
  std::vector<dcp::Lin> island_pos, export_pos, attraction_pos;
  for (const auto& r : island) island_pos.push_back(position(r));
  for (const auto& r : exports) export_pos.push_back(position(r));
  for (const auto& r : attraction) attraction_pos.push_back(position(r));
  out.add("island", island_pos);
  out.add("export", export_pos);
  out.add("attraction", attraction_pos);
}
