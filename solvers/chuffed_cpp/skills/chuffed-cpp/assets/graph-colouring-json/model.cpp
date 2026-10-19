// Graph colouring: give every node a colour so that neighbours differ, using as few colours
// as possible. The graph is read from a JSON file: model [data.json]
//
// JSON library: nlohmann/json (header only; apt install nlohmann-json3-dev,
// brew install nlohmann-json, or vcpkg/conan nlohmann-json).
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <ostream>
#include <vector>

using nlohmann::json;

class Colouring : public Problem {
 public:
  int n;
  vec<IntVar*> colour;  // colour[v] in 0..n-1
  IntVar* top;          // the highest colour used; colours used = top + 1

  explicit Colouring(const std::vector<std::vector<int>>& neighbours)
      : n(static_cast<int>(neighbours.size())) {
    createVars(colour, n, 0, n - 1);

    // adjacent nodes get different colours (each edge once: v < w)
    for (int v = 0; v < n; ++v)
      for (int w : neighbours[v])
        if (v < w) int_rel(colour[v], IRT_NE, colour[w]);

    // top is the largest colour; colours are interchangeable, so node 0 takes colour 0
    top = newIntVar(0, n - 1);
    maximum(colour, top);
    int_rel(colour[0], IRT_EQ, 0);

    branch(colour, VAR_SIZE_MIN, VAL_MIN);
    optimize(top, OPT_MIN);
  }

  void print(std::ostream& os) override {
    os << "colours " << top->getVal() + 1 << ":";
    for (int v = 0; v < n; ++v) os << ' ' << colour[v]->getVal();
    os << "\n";
  }
};

int main(int argc, char** argv) {
  const char* path = argc > 1 ? argv[1] : "data.json";
  std::ifstream in(path);
  if (!in) {
    std::cerr << "cannot open " << path << "\n";
    return 2;
  }
  json data = json::parse(in);  // throws json::parse_error on malformed input

  // Every size comes from the data. "neighbours" is ragged: one list per node, any length.
  // Keys this program does not use (such as "name") are ignored.
  auto neighbours = data.at("neighbours").get<std::vector<std::vector<int>>>();
  std::cout << "graph " << data.value("name", "unnamed") << ", " << neighbours.size()
            << " nodes" << std::endl;

  so.print_sol = true;
  engine.solve(new Colouring(neighbours));
  if (engine.status == RES_UNK)
    std::cout << "Time out, best found: " << engine.best_sol + 1 << " colours" << std::endl;
  else if (engine.solutions == 0)
    std::cout << "Infeasible" << std::endl;
  else
    std::cout << "Minimum colours: " << engine.best_sol + 1 << std::endl;
  return 0;
}
