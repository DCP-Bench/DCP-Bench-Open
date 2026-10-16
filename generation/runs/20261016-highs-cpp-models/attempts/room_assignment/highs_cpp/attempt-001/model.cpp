// Room assignment: each request is a stay from its start date up to, but not including, its
// end date. Every request gets exactly one room, numbered 0 to max_rooms - 1. A room serves at
// most one request at a time, so two requests whose stays overlap never share a room. A request
// with a pre-assigned room (preassigned_room_data, -1 for none) keeps that room. The output
// room_assignments gives each request's room.
#include "dcp.h"

namespace {

// Day number of a date written YYYY-MM-DD (days since 1970-01-01, proleptic Gregorian calendar).
long long day_number(const std::string& date) {
  long long y = std::stoll(date.substr(0, 4));
  long long m = std::stoll(date.substr(5, 2));
  long long d = std::stoll(date.substr(8, 2));
  y -= m <= 2 ? 1 : 0;
  long long era = (y >= 0 ? y : y - 399) / 400;
  long long yoe = y - era * 400;
  long long doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  long long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + doe - 719468;
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& start_data = instance.at("start_data");
  const auto& end_data = instance.at("end_data");
  const auto& preassigned = instance.at("preassigned_room_data");
  const int n = static_cast<int>(start_data.size());
  const int max_rooms = instance.at("max_rooms").get<int>();

  std::vector<long long> start(n), end(n);
  for (int i = 0; i < n; ++i) {
    start[i] = day_number(start_data[i].get<std::string>());
    end[i] = day_number(end_data[i].get<std::string>());
  }

  // x[i][r] = 1 when request i is in room r.
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(max_rooms));
  for (int i = 0; i < n; ++i)
    for (int r = 0; r < max_rooms; ++r) x[i][r] = dcp::new_var(h, 0, 1);

  // each request is in exactly one room
  for (int i = 0; i < n; ++i) {
    dcp::Lin one_room;
    for (int r = 0; r < max_rooms; ++r) one_room = one_room + x[i][r];
    dcp::add_row(h, one_room, 1, 1);
  }

  // a pre-assigned request is in its given room
  for (int i = 0; i < n; ++i) {
    int p = preassigned[i].get<int>();
    if (p < 0) continue;
    if (p >= max_rooms) throw std::runtime_error("pre-assigned room is out of range");
    dcp::add_row(h, x[i][p], 1, 1);
  }

  // Two stays overlap when they share a night. Stays are intervals, so the stays that
  // overlap pairwise share a common night: the latest start among them. For each request i,
  // the requests whose stay covers the night start_i (i itself included) share that night,
  // so each room takes at most one of them.
  // This assumes every stay has end > start, which holds for all instances.
  for (int i = 0; i < n; ++i) {
    for (int r = 0; r < max_rooms; ++r) {
      // the requests staying on the night start_i that are in room r
      dcp::Lin sharing;
      for (int j = 0; j < n; ++j)
        if (start[j] <= start[i] && start[i] < end[j]) sharing = sharing + x[j][r];
      dcp::add_row(h, sharing, -kHighsInf, 1);
    }
  }

  // room_assignments[i] = the room number of request i
  std::vector<dcp::Lin> room_assignments(n);
  for (int i = 0; i < n; ++i)
    for (int r = 0; r < max_rooms; ++r)
      room_assignments[i] = room_assignments[i] + static_cast<double>(r) * x[i][r];
  out.add("room_assignments", room_assignments);
}
