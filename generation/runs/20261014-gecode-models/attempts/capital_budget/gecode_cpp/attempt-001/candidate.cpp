#include "dcp.h"

// Capital budgeting: a company chooses which of its investments to make. Each
// investment has a net present value (NPV) and requires a cash outflow today.
// The total cash outflow of the chosen investments must not exceed the budget.
// Maximise the total NPV of the chosen investments.
class CapitalBudget : public dcp::Space {
 protected:
  BoolVarArray x;  // x[i] = 1 if investment i is chosen
  IntVar z;        // total NPV of the chosen investments

 public:
  explicit CapitalBudget(const json& instance) {
    int budget = instance.at("budget").get<int>();
    std::vector<int> npv = instance.at("npv").get<std::vector<int>>();
    std::vector<int> cash_flow = instance.at("cash_flow").get<std::vector<int>>();
    int n = static_cast<int>(npv.size());

    int total_npv = 0;
    for (int v : npv) total_npv += v;

    // each investment is either chosen or not
    x = BoolVarArray(*this, n, 0, 1);
    z = IntVar(*this, 0, total_npv);

    // the sum of the cash outflows of all chosen investments is within the budget
    linear(*this, IntArgs(cash_flow), x, IRT_LQ, budget);

    // total NPV is the sum of the NPVs of the chosen investments
    linear(*this, IntArgs(npv), x, IRT_EQ, z, IPL_DOM);

    // decide each investment, trying to choose it first (it adds NPV)
    branch(*this, x, BOOL_VAR_NONE(), BOOL_VAL_MAX());

    maximize(z);
    output("x", x);
    output("z", z);
  }

  CapitalBudget(CapitalBudget& s) : dcp::Space(s) {
    x.update(*this, s.x);
    z.update(*this, s.z);
  }
  Gecode::Space* copy() override { return new CapitalBudget(*this); }
};

DCP_MODEL(CapitalBudget)
