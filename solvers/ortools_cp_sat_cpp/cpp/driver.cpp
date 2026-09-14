#include <chrono>
#include <iostream>
#include <set>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Generated source implements this function. Output leaves are IntVar indices;
// use integer 0/1 variables for Boolean outputs and auxiliary vars for expressions.
void Build(const json& instance, CpModelBuilder& model, json& outputs);

json Read(const json& layout, const CpSolverResponse& response, std::vector<int>& indices) {
  if (layout.is_object()) {
    json result = json::object();
    for (auto it = layout.begin(); it != layout.end(); ++it) result[it.key()] = Read(it.value(), response, indices);
    return result;
  }
  if (layout.is_array()) {
    json result = json::array();
    for (const auto& item : layout) result.push_back(Read(item, response, indices));
    return result;
  }
  if (!layout.is_number_integer()) throw std::runtime_error("Output leaves must be variable indices");
  int index = layout.get<int>();
  if (index < 0 || index >= response.solution_size()) throw std::runtime_error("Invalid output variable index");
  indices.push_back(index);
  return response.solution(index);
}

void Status(const std::string& status, double seconds, const std::string& detail = "") {
  std::cout << json({{"type", "status"}, {"status", status}, {"solve_seconds", seconds}, {"detail", detail}}).dump() << std::endl;
}

int main() {
  try {
    json request; std::cin >> request;
    CpModelBuilder model; json outputs;
    Build(request.at("instance"), model, outputs);
    if (model.Build().has_floating_point_objective()) { Status("unsupported", 0, "Use an integer objective"); return 0; }
    if (!outputs.is_object() || outputs.empty()) throw std::runtime_error("Expected output dictionary");
    auto start = std::chrono::steady_clock::now();
    double seconds = 0;
    int count = 0, limit = request.at("solution_limit");
    while (count < limit) {
      double left = request.at("execution_timeout").get<double>() - std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
      if (left <= 0) { Status("timeout", seconds); return 0; }
      SatParameters params; params.set_max_time_in_seconds(left); params.set_num_search_workers(1);
      const auto response = SolveWithParameters(model.Build(), params);
      seconds += response.wall_time();
      if (response.status() == CpSolverStatus::INFEASIBLE) { Status(count ? "complete" : "unsat", seconds); return 0; }
      if (response.status() == CpSolverStatus::MODEL_INVALID) { Status("error", seconds, "Invalid CP-SAT model"); return 0; }
      if ((response.status() != CpSolverStatus::OPTIMAL && response.status() != CpSolverStatus::FEASIBLE) ||
          (model.Build().has_objective() && response.status() != CpSolverStatus::OPTIMAL)) {
        Status("timeout", seconds); return 0;
      }
      std::vector<int> indices;
      json values = Read(outputs, response, indices);
      std::cout << json({{"type", "solution"}, {"values", values}}).dump() << std::endl;
      ++count;
      if (count == limit) break;
      if (model.Build().has_floating_point_objective()) { Status("unsupported", seconds, "Use an integer objective"); return 0; }
      if (model.Build().has_objective()) {
        auto obj = model.Build().objective();
        LinearExpr expression;
        for (int i = 0; i < obj.vars_size(); ++i) expression += model.GetIntVarFromProtoIndex(obj.vars(i)) * obj.coeffs(i);
        int64_t value = 0;
        for (int i = 0; i < obj.vars_size(); ++i) value += response.solution(obj.vars(i)) * obj.coeffs(i);
        model.ClearObjective(); model.AddEquality(expression, value);
      }
      std::vector<IntVar> vars; std::vector<int64_t> tuple;
      std::set<int> unique(indices.begin(), indices.end());
      for (int index : unique) { vars.push_back(model.GetIntVarFromProtoIndex(index)); tuple.push_back(response.solution(index)); }
      model.AddForbiddenAssignments(vars).AddTuple(tuple);
    }
    Status("limit", seconds);
  } catch (const std::exception& error) { Status("error", 0, error.what()); }
}
