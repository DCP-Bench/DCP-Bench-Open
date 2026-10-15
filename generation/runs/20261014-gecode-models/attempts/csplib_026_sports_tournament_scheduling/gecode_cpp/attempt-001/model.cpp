#include "dcp.h"

// Sports tournament scheduling: n teams play over n-1 weeks. Each week has n/2
// periods of two slots; the first team in a slot plays at home, the second away.
// Every team plays once a week, at most twice in the same period, and every
// team plays every other team exactly once.
class SportsTournament : public dcp::Space {
 protected:
  int n;                // number of teams (from the instance)
  IntVarArray sl;       // sl[w*n + s]: team in slot s of week w (s = 2p home, 2p+1 away)
  IntVarArray ps;       // ps[w*n + t]: slot of team t in week w (inverse of sl)
  IntVarArray opp;      // opp[w*n + t]: opponent of team t in week w

 public:
  explicit SportsTournament(const json& instance) {
    n = instance.at("n_teams").get<int>();
    int weeks = n - 1;
    int periods = n / 2;

    sl = IntVarArray(*this, weeks * n, 0, n - 1);
    ps = IntVarArray(*this, weeks * n, 0, n - 1);
    opp = IntVarArray(*this, weeks * n, 0, n - 1);

    // slot s is paired with slot s xor 1 (home and away of the same period)
    IntArgs partner(n);
    for (int s = 0; s < n; ++s) partner[s] = s ^ 1;

    for (int w = 0; w < weeks; ++w) {
      IntVarArgs slots;
      for (int s = 0; s < n; ++s) slots << sl[w * n + s];

      // every team plays once a week
      distinct(*this, slots, IPL_DOM);

      // link the team-to-slot view of the week with the slot-to-team view
      IntVarArgs where;
      for (int t = 0; t < n; ++t) where << ps[w * n + t];
      channel(*this, slots, where, IPL_DOM);

      // the opponent of a team is the team in its paired slot
      IntVarArgs opps;
      for (int t = 0; t < n; ++t) {
        IntVar pslot(*this, 0, n - 1);
        element(*this, partner, ps[w * n + t], pslot);
        element(*this, slots, pslot, opp[w * n + t]);
        opps << opp[w * n + t];
      }

      // playing is mutual: the opponent of my opponent is me
      for (int t = 0; t < n; ++t) {
        IntVar back(*this, 0, n - 1);
        element(*this, opps, opp[w * n + t], back);
        rel(*this, back == t);
      }
    }

    // symmetry breaking: teams can be renamed freely, so week 1 can be fixed to
    // 1 v 2, 3 v 4, ... (team s+1 in slot s); this keeps every schedule up to renaming
    for (int s = 0; s < n; ++s) rel(*this, sl[s] == s);

    // every team plays every other team: its n-1 opponents are all different
    for (int t = 0; t < n; ++t) {
      IntVarArgs opponents;
      for (int w = 0; w < weeks; ++w) opponents << opp[w * n + t];
      distinct(*this, opponents, IPL_DOM);
    }

    // every team plays at most twice in the same period over the tournament
    for (int p = 0; p < periods; ++p) {
      IntVarArgs period;
      for (int w = 0; w < weeks; ++w) {
        period << sl[w * n + 2 * p] << sl[w * n + 2 * p + 1];
      }
      for (int t = 0; t < n; ++t) count(*this, period, t, IRT_LQ, 2);
    }

    // slots chosen by activity with Luby restarts: the search is heavy-tailed
    restarts(100);
    branch(*this, sl, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    branch(*this, ps, INT_VAR_NONE(), INT_VAL_MIN());

    // outputs: home[w][p] and away[w][p], teams numbered 1..n as the description asks
    std::vector<IntVarArgs> home(weeks), away(weeks);
    for (int w = 0; w < weeks; ++w) {
      for (int p = 0; p < periods; ++p) {
        home[w] << expr(*this, sl[w * n + 2 * p] + 1);
        away[w] << expr(*this, sl[w * n + 2 * p + 1] + 1);
      }
    }
    output("home", home);
    output("away", away);
  }

  SportsTournament(SportsTournament& s) : dcp::Space(s), n(s.n) {
    sl.update(*this, s.sl);
    ps.update(*this, s.ps);
    opp.update(*this, s.opp);
  }
  Gecode::Space* copy() override { return new SportsTournament(*this); }
};

DCP_MODEL(SportsTournament)
