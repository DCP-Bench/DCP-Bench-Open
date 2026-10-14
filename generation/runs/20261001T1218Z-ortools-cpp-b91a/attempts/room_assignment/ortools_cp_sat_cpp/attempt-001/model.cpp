#include <algorithm>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

namespace {

// Day number of a "YYYY-MM-DD" date (days since 1970-01-01, proleptic Gregorian
// calendar), so that dates can be compared and subtracted as integers.
int64_t DayNumber(const std::string& date) {
  int64_t y = std::stoi(date.substr(0, 4));
  const int64_t m = std::stoi(date.substr(5, 2));
  const int64_t d = std::stoi(date.substr(8, 2));
  y -= m <= 2;
  const int64_t era = (y >= 0 ? y : y - 399) / 400;
  const int64_t yoe = y - era * 400;
  const int64_t doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  const int64_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + doe - 719468;
}

}  // namespace

// Room assignment: give every request (a stay from a start date up to, but not
// including, an end date) one room for its whole stay, so that no room serves
// two requests on the same day. Some requests already have a room.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t max_rooms = instance.at("max_rooms").get<int64_t>();
  const std::vector<std::string> start_data = instance.at("start_data").get<std::vector<std::string>>();
  const std::vector<std::string> end_data = instance.at("end_data").get<std::vector<std::string>>();
  // preassigned_room_data[i] is the room already given to request i, or -1 for none.
  const std::vector<int64_t> preassigned_room =
      instance.at("preassigned_room_data").get<std::vector<int64_t>>();
  const int n_requests = static_cast<int>(start_data.size());

  std::vector<int64_t> start(n_requests), end(n_requests);
  for (int i = 0; i < n_requests; ++i) {
    start[i] = DayNumber(start_data[i]);
    end[i] = DayNumber(end_data[i]);
  }

  // requestvars[i] is the room (0 .. max_rooms - 1) of request i, kept for
  // the whole period of the request.
  std::vector<IntVar> requestvars;
  for (int i = 0; i < n_requests; ++i) requestvars.push_back(model.NewIntVar(Domain(0, max_rooms - 1)));

  // Some requests already have a room pre-assigned.
  for (int i = 0; i < n_requests; ++i)
    if (preassigned_room[i] != -1) model.AddEquality(requestvars[i], preassigned_room[i]);

  // A room can only serve one request at a time. Two requests are on the same
  // day when some day d has start <= d < end for both, i.e. when the later of
  // the two starts is before the earlier of the two ends. Such requests must be
  // in different rooms (equivalent to the reference's all-different over the
  // requests present on each day).
  for (int i = 0; i < n_requests; ++i) {
    for (int j = i + 1; j < n_requests; ++j) {
      if (std::max(start[i], start[j]) < std::min(end[i], end[j])) {
        model.AddNotEqual(requestvars[i], requestvars[j]);
      }
    }
  }

  json out = json::array();
  for (const IntVar& v : requestvars) out.push_back(v.index());
  outputs = {{"room_assignments", out}};
}
