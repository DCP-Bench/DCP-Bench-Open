#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Fancy dress party: Mr Greenguest must follow Mr Greenfan's green-dress rules
// or pay an $11 entrance fee. He owns a green shirt; a tie costs $10, a hat $2
// and socks $12. Find his cheapest way in.
// The problem has no instance data; the prices come from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const BoolVar t = model.NewBoolVar();  // wears a green tie
  const BoolVar h = model.NewBoolVar();  // wears a green hat
  const BoolVar r = model.NewBoolVar();  // wears a green shirt
  const BoolVar s = model.NewBoolVar();  // wears green socks
  const BoolVar n = model.NewBoolVar();  // pays the entrance fee

  // Rule 1: a green tie requires a green shirt, unless the fee is paid.
  // (t -> r) | n  is  ~t | r | n.
  model.AddBoolOr({t.Not(), r, n});

  // Rule 2: green socks or a green shirt only with a green tie or a green hat,
  // unless the fee is paid. ((s | r) -> (t | h)) | n splits into one clause for
  // s and one for r.
  model.AddBoolOr({s.Not(), t, h, n});
  model.AddBoolOr({r.Not(), t, h, n});

  // Rule 3: a green shirt, a green hat, or no green socks requires a green tie,
  // otherwise the fee is paid. (r | h | ~s) -> (t | n) splits into three clauses.
  model.AddBoolOr({r.Not(), t, n});
  model.AddBoolOr({h.Not(), t, n});
  model.AddBoolOr({s, t, n});

  // Rule 4 and the prices: cost = 10 tie + 2 hat + 12 socks + 11 fee, minimised.
  // The shirt is already owned and costs nothing.
  model.Minimize(10 * t + 2 * h + 12 * s + 11 * n);

  outputs = {{"t", t.index()}, {"h", h.index()}, {"r", r.index()}, {"s", s.index()},
             {"n", n.index()}};
}
