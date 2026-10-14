#include "dcp.h"

// Progressive party problem: a yacht club party. Some boats are hosts; the crews of the
// other (guest) boats visit the host boats over several periods. Minimise the number
// of host boats.
class ProgressiveParty : public dcp::Space {
 protected:
  int n;               // number of boats
  int P;               // number of periods
  BoolVarArray host;   // host[b]: boat b is a host boat
  IntVarArray visits;  // visits[p*n+b]: in period p, boat b is at boat visits[p*n+b]
  IntVar n_hosts;      // total number of host boats (the objective)

 public:
  explicit ProgressiveParty(const json& instance) {
    n = instance.at("n_boats").get<int>();
    P = instance.at("n_periods").get<int>();
    std::vector<int> capacity = instance.at("capacity").get<std::vector<int>>();
    std::vector<int> crew = instance.at("crew_size").get<std::vector<int>>();

    host = BoolVarArray(*this, n, 0, 1);
    visits = IntVarArray(*this, P * n, 0, n - 1);

    BoolVarArgs hostArgs;
    for (int b = 0; b < n; ++b) hostArgs << host[b];

    // a host boat stays on board: in every period its own crew is the one visiting it
    for (int p = 0; p < P; ++p)
      for (int b = 0; b < n; ++b) {
        rel(*this, (host[b] == 1) >> (visits[p * n + b] == b));
        rel(*this, (host[b] == 0) >> (visits[p * n + b] != b));
      }

    // a guest boat visits a host boat in every period; it does not visit itself
    for (int p = 0; p < P; ++p)
      for (int b = 0; b < n; ++b)
        element(*this, hostArgs, visits[p * n + b], 1);

    // a guest boat cannot revisit a host: its visits over the periods are all different
    // (host boats are not selected, they stay at their own boat)
    for (int b = 0; b < n; ++b) {
      BoolVarArgs isGuest;
      IntVarArgs seen;
      for (int p = 0; p < P; ++p) {
        isGuest << expr(*this, host[b] == 0);
        seen << visits[p * n + b];
      }
      distinct(*this, isGuest, seen, IPL_DOM);
    }

    // the people aboard a host boat, its own crew and the guest crews, stay within its
    // capacity in every period. A boat that is not a host receives no visits.
    for (int p = 0; p < P; ++p)
      for (int h = 0; h < n; ++h) {
        BoolVarArgs atHost;
        for (int g = 0; g < n; ++g) atHost << expr(*this, visits[p * n + g] == h);
        linear(*this, IntArgs(crew), atHost, IRT_LQ, capacity[h]);
      }

    // crews cannot meet more than once: two boats share a host boat in at most one period
    for (int a = 0; a < n; ++a)
      for (int b = a + 1; b < n; ++b) {
        BoolVarArgs together;
        for (int p = 0; p < P; ++p)
          together << expr(*this, visits[p * n + a] == visits[p * n + b]);
        linear(*this, together, IRT_LQ, 1);
      }

    // minimise the number of host boats
    n_hosts = expr(*this, sum(hostArgs));
    minimize(n_hosts);

    // branch on the host boats first, trying "not a host" first, then on the visits
    branch(*this, hostArgs, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    IntVarArgs visitArgs;
    for (int i = 0; i < P * n; ++i) visitArgs << visits[i];
    branch(*this, visitArgs, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    Matrix<IntVarArray> visitMatrix(visits, n, P);
    output("is_host", host);
    output("visits", visitMatrix);
  }

  ProgressiveParty(ProgressiveParty& s) : dcp::Space(s), n(s.n), P(s.P) {
    host.update(*this, s.host);
    visits.update(*this, s.visits);
    n_hosts.update(*this, s.n_hosts);
  }
  Gecode::Space* copy() override { return new ProgressiveParty(*this); }
};

DCP_MODEL(ProgressiveParty)
