#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Handshaking: Hilary and Jocelyn (a couple) host num_couples other couples.
// Everybody shakes hands with some of the others, never with themselves or
// their spouse. Everybody except Hilary reports a different number of
// handshakes. Find how many hands Hilary shook.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_couples = instance.at("num_couples").get<int>();
  // Persons are numbered so that couples are neighbours: (0,1), (2,3), ...
  // Hilary is person 0 and Jocelyn is person 1.
  const int n = 2 + num_couples * 2;

  // x[i] is the number of hands person i has shaken; at most n - 2, since
  // nobody shakes with themselves or their spouse.
  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, n - 2)));

  // shake[i][j] is true when persons i and j shake hands. One Boolean per
  // pair is shared by shake[i][j] and shake[j][i], which states that
  // handshaking is mutual (i shakes with j exactly when j shakes with i)
  // without a second variable and an equality. Nobody shakes hands with
  // themselves or with their spouse, so those pairs have no variable and
  // count as 0.
  std::vector<std::vector<BoolVar>> shake(n, std::vector<BoolVar>(n));
  std::vector<std::vector<bool>> may_shake(n, std::vector<bool>(n, false));
  LinearExpr all_handshakes;
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      if (j == i + 1 && i % 2 == 0) continue;  // spouses: persons 2k and 2k+1
      const BoolVar b = model.NewBoolVar();
      shake[i][j] = b;
      shake[j][i] = b;
      may_shake[i][j] = may_shake[j][i] = true;
      all_handshakes += b;
    }
  }

  // x[i] counts the hands person i has shaken.
  LinearExpr total_hands;
  for (int i = 0; i < n; ++i) {
    LinearExpr shaken;
    for (int j = 0; j < n; ++j)
      if (may_shake[i][j]) shaken += shake[i][j];
    model.AddEquality(x[i], shaken);
    total_hands += x[i];
  }

  // The answers of everybody except Hilary are all different.
  model.AddAllDifferent(std::vector<IntVar>(x.begin() + 1, x.end()));

  // Every handshake is counted by both persons, so the hand counts add up to
  // twice the number of handshakes (an implied constraint; it lets the solver
  // see that the total of the counts is even).
  const IntVar handshakes = model.NewIntVar(Domain(0, static_cast<int64_t>(n) * (n - 1) / 2));
  model.AddEquality(handshakes, all_handshakes);
  model.AddEquality(total_hands, 2 * handshakes);

  // Symmetry breaking. The guest couples (persons 2c and 2c+1 for c = 1..num_couples)
  // are interchangeable, and so are the two partners of a couple: swapping
  // them in a solution gives another solution with the same counts for
  // Hilary and Jocelyn. All guests have different counts, so each solution
  // has one labelling in which the partner with the smaller count comes first
  // in every couple and the couples are listed by increasing count of that
  // first partner. Requiring this removes only relabelled copies of a
  // solution, so the set of possible values of Hilary's count (the output)
  // is unchanged.
  for (int c = 1; c <= num_couples; ++c) {
    model.AddLessThan(x[2 * c], x[2 * c + 1]);
    if (c < num_couples) model.AddLessThan(x[2 * c], x[2 * c + 2]);
  }

  // hil is the number of hands Hilary (person 0) has shaken.
  outputs = {{"hil", x[0].index()}};
}
