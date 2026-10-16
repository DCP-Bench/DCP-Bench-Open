// Solitaire battleships (csplib 014). Place the fleet on a rows x cols grid so that the
// row and column counts of occupied squares hold, the hinted squares have their kinds,
// and the fleet rules hold: the fleet_counts give how many ships of each length, every
// ship is a straight line of squares, and no two ships touch, not even diagonally.
// The grid output gives each square's kind: water, submarine (circle), or a ship part
// (left, right, top, bottom, middle).
//
// Encoding: one binary per possible placement of a ship (a length, a top-left square and
// an orientation). Squares are occupied by the placements that cover them.
#include "dcp.h"

#include <set>
#include <utility>
#include <vector>

namespace {

// One way to place a ship: its squares and the kind of each square, in the same order.
struct Placement {
  int length;
  std::vector<std::pair<int, int>> squares;
  std::vector<int> parts;
};

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int rows = instance.at("rows").get<int>();
  const int cols = instance.at("cols").get<int>();
  const int water = instance.at("WATER").get<int>();
  const int circle = instance.at("CIRCLE").get<int>();
  const int left = instance.at("LEFT").get<int>();
  const int right = instance.at("RIGHT").get<int>();
  const int top = instance.at("TOP").get<int>();
  const int bottom = instance.at("BOTTOM").get<int>();
  const int middle = instance.at("MIDDLE").get<int>();
  const json& fleet = instance.at("fleet_counts");  // [length, count] pairs

  // Every placement of a ship of each length in the fleet. A ship of length 1 is a
  // submarine: one square, one placement per square (no orientation).
  std::vector<Placement> placements;
  for (const auto& entry : fleet) {
    const int length = entry[0].get<int>();
    for (int r = 0; r < rows; ++r) {
      for (int c = 0; c < cols; ++c) {
        if (length == 1) {
          placements.push_back({1, {{r, c}}, {circle}});
          continue;
        }
        // A horizontal ship starting at (r, c): left end, middle squares, right end.
        if (c + length <= cols) {
          Placement p{length, {}, {}};
          for (int k = 0; k < length; ++k) {
            p.squares.push_back({r, c + k});
            p.parts.push_back(k == 0 ? left : (k == length - 1 ? right : middle));
          }
          placements.push_back(p);
        }
        // A vertical ship starting at (r, c): top end, middle squares, bottom end.
        if (r + length <= rows) {
          Placement p{length, {}, {}};
          for (int k = 0; k < length; ++k) {
            p.squares.push_back({r + k, c});
            p.parts.push_back(k == 0 ? top : (k == length - 1 ? bottom : middle));
          }
          placements.push_back(p);
        }
      }
    }
  }

  // One binary per placement: 1 means this ship is placed.
  std::vector<dcp::Lin> ship;
  for (size_t k = 0; k < placements.size(); ++k) ship.push_back(dcp::new_var(h, 0, 1));

  // For each square, the placements that cover it, with the kind the placement gives it.
  std::vector<std::vector<std::vector<std::pair<size_t, int>>>> covering(
      rows, std::vector<std::vector<std::pair<size_t, int>>>(cols));
  for (size_t k = 0; k < placements.size(); ++k)
    for (size_t s = 0; s < placements[k].squares.size(); ++s) {
      const auto [r, c] = placements[k].squares[s];
      covering[r][c].push_back({k, placements[k].parts[s]});
    }

  // Whether a square is occupied by a ship (at most one ship covers it, see below).
  auto occupied = [&](int r, int c) {
    dcp::Lin e;
    for (const auto& [k, part] : covering[r][c]) e = e + ship[k];
    return e;
  };
  // The kind of a square: water, or the kind of the ship covering it.
  auto kind = [&](int r, int c) {
    dcp::Lin e(water);
    for (const auto& [k, part] : covering[r][c]) e = e + static_cast<double>(part - water) * ship[k];
    return e;
  };

  // Ships do not share a square: each square holds at most one ship.
  for (int r = 0; r < rows; ++r)
    for (int c = 0; c < cols; ++c) dcp::add_row(h, occupied(r, c), 0, 1);

  // The fleet has exactly the given number of ships of each length.
  for (const auto& entry : fleet) {
    const int length = entry[0].get<int>();
    const int count = entry[1].get<int>();
    dcp::Lin total;
    for (size_t k = 0; k < placements.size(); ++k)
      if (placements[k].length == length) total = total + ship[k];
    dcp::add_row(h, total, count, count);
  }

  // Row sums: the number of occupied squares in each row is the row's count.
  const json& rowsum = instance.at("rowsum");
  for (int r = 0; r < rows; ++r) {
    dcp::Lin total;
    for (int c = 0; c < cols; ++c) total = total + occupied(r, c);
    const int count = rowsum[r].get<int>();
    dcp::add_row(h, total, count, count);
  }

  // Column sums: the number of occupied squares in each column is the column's count.
  const json& colsum = instance.at("colsum");
  for (int c = 0; c < cols; ++c) {
    dcp::Lin total;
    for (int r = 0; r < rows; ++r) total = total + occupied(r, c);
    const int count = colsum[c].get<int>();
    dcp::add_row(h, total, count, count);
  }

  // Ships do not touch, not even diagonally: a square next to a placed ship (and not part
  // of it) is not occupied by another ship. Each square around a placement is checked
  // against the placement with one row: ship + occupied(square) <= 1.
  for (size_t k = 0; k < placements.size(); ++k) {
    std::set<std::pair<int, int>> own(placements[k].squares.begin(), placements[k].squares.end());
    std::set<std::pair<int, int>> around;
    for (const auto& [r, c] : placements[k].squares)
      for (int dr = -1; dr <= 1; ++dr)
        for (int dc = -1; dc <= 1; ++dc) {
          const int nr = r + dr, nc = c + dc;
          if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
          if (own.count({nr, nc})) continue;
          around.insert({nr, nc});
        }
    for (const auto& [nr, nc] : around)
      dcp::add_row(h, ship[k] + occupied(nr, nc), -kHighsInf, 1);
  }

  // Hints: the hinted squares have the hinted kind, given as [row, col, kind].
  for (const auto& hint : instance.at("hints")) {
    const int r = hint[0].get<int>();
    const int c = hint[1].get<int>();
    const int code = hint[2].get<int>();
    dcp::add_row(h, kind(r, c), code, code);
  }

  // The output grid: the kind of each square.
  std::vector<std::vector<dcp::Lin>> grid(rows, std::vector<dcp::Lin>(cols));
  for (int r = 0; r < rows; ++r)
    for (int c = 0; c < cols; ++c) grid[r][c] = kind(r, c);
  out.add("grid", grid);
}
