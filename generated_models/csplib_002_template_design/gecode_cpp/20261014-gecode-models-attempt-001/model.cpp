#include "dcp.h"

// Template design (CSPLib 002): a colour printer prints several design variations
// of one carton from a small number of templates. Each template has n_slots
// positions, each holding one copy of a variation. Each template is printed
// production[t] times. Every variation must be printed at least its demand in
// total. Minimise the total number of printed sheets.
class TemplateDesign : public dcp::Space {
 protected:
  int T;                   // number of templates (n_templates)
  int V;                   // number of design variations (n_var)
  int S;                   // positions on each template (n_slots)
  IntVarArray layout;      // layout[t * V + v]: copies of variation v on template t
  IntVarArray printed;     // printed[t * V + v] = production[t] * layout[t * V + v]
  IntVarArray production;  // production[t]: sheets printed from template t
  IntVar total;            // total number of printed sheets

 public:
  explicit TemplateDesign(const json& instance) {
    S = instance.at("n_slots").get<int>();
    T = instance.at("n_templates").get<int>();
    V = instance.at("n_var").get<int>();
    std::vector<int> demand = instance.at("demand").get<std::vector<int>>();

    int maxDemand = 0;
    int demandSum = 0;
    for (int d : demand) {
      maxDemand = d > maxDemand ? d : maxDemand;
      demandSum += d;
    }

    layout = IntVarArray(*this, T * V, 0, S);
    // A sheet printed more than the largest demand over-supplies every variation
    // on it, so this bound loses no optimal solution.
    production = IntVarArray(*this, T, 0, maxDemand);
    // copies of v printed from t = sheets of t times copies of v on t: at most maxDemand * n_slots
    printed = IntVarArray(*this, T * V, 0, S * maxDemand);
    for (int t = 0; t < T; ++t)
      for (int v = 0; v < V; ++v)
        rel(*this, printed[t * V + v] == production[t] * layout[t * V + v]);

    // every template is full: its n_slots positions hold one copy each
    for (int t = 0; t < T; ++t) {
      IntVarArgs row;
      for (int v = 0; v < V; ++v) row << layout[t * V + v];
      linear(*this, row, IRT_EQ, S);
    }

    // the copies printed from template t are its n_slots positions times its
    // sheets (implied by the full-template rule; links the products to the sheets)
    for (int t = 0; t < T; ++t) {
      IntVarArgs vars;
      IntArgs coef;
      for (int v = 0; v < V; ++v) {
        vars << printed[t * V + v];
        coef << 1;
      }
      vars << production[t];
      coef << -S;
      linear(*this, coef, vars, IRT_EQ, 0);
    }

    // each variation is printed at least its demand, summed over the templates
    for (int v = 0; v < V; ++v) {
      IntVarArgs column;
      for (int t = 0; t < T; ++t) column << printed[t * V + v];
      linear(*this, column, IRT_GQ, demand[v]);
    }

    // templates are interchangeable: order them by their layout rows
    // (lexicographic order on consecutive rows, valid since permuting templates
    // keeps every constraint and the objective)
    for (int t = 0; t + 1 < T; ++t) {
      IntVarArgs a, b;
      for (int v = 0; v < V; ++v) {
        a << layout[t * V + v];
        b << layout[(t + 1) * V + v];
      }
      rel(*this, a, IRT_LQ, b);
    }

    // minimise the total number of printed sheets
    IntVarArgs sheets;
    for (int t = 0; t < T; ++t) sheets << production[t];
    total = expr(*this, sum(sheets));
    // every sheet carries at most n_slots copies and all demand must be printed,
    // so the sheets are at least the total demand over n_slots (implied; rounded up)
    linear(*this, sheets, IRT_GQ, (demandSum + S - 1) / S);

    // the other variations are printed at least their demand, so variation v can
    // only take the copies left over: copies of v <= S * sheets - (demand of the others)
    // (implied by the rules above; it prunes the search, it removes no solution)
    for (int v = 0; v < V; ++v) {
      IntVarArgs vars;
      IntArgs coef;
      for (int t = 0; t < T; ++t) {
        vars << printed[t * V + v];
        coef << 1;
      }
      for (int t = 0; t < T; ++t) {
        vars << production[t];
        coef << -S;
      }
      linear(*this, coef, vars, IRT_LQ, demand[v] - demandSum);
    }

    branch(*this, production, INT_VAR_SIZE_MIN(), INT_VAL_SPLIT_MIN());
    branch(*this, layout, INT_VAR_SIZE_MIN(), INT_VAL_MAX());
    minimize(total);

    output("layout", Matrix<IntVarArray>(layout, V, T));
    output("production", production);
  }

  TemplateDesign(TemplateDesign& s) : dcp::Space(s), T(s.T), V(s.V), S(s.S) {
    layout.update(*this, s.layout);
    printed.update(*this, s.printed);
    production.update(*this, s.production);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new TemplateDesign(*this); }
};

DCP_MODEL(TemplateDesign)
