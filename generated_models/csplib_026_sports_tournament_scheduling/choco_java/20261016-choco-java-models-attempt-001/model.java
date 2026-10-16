import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Sports tournament scheduling: n teams play over n-1 weeks, each week split into n/2 periods
// with a home team and an away team per period, such that every team plays once a week,
// at most twice in the same period, and every team plays every other team once.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_teams");
    int weeks = n - 1;
    int periods = n / 2;

    // home[w][p] and away[w][p] are the two teams in period p of week w (teams numbered 1..n)
    IntVar[][] home = m.intVarMatrix("home", weeks, periods, 1, n);
    IntVar[][] away = m.intVarMatrix("away", weeks, periods, 1, n);

    // slot[w][s] is the team in slot s of week w: slot 2p is the home team of period p, 2p+1 the away team
    IntVar[][] slot = new IntVar[weeks][n];
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        slot[w][2 * p] = home[w][p];
        slot[w][2 * p + 1] = away[w][p];
      }
    }

    // every team plays once a week, and slotOf[w][t] is the slot where team t+1 plays in week w
    IntVar[][] slotOf = new IntVar[weeks][n];
    for (int w = 0; w < weeks; w++) {
      m.allDifferent(slot[w], "AC").post();
      for (int t = 0; t < n; t++) {
        slotOf[w][t] = m.intVar("slotOf_" + w + "_" + t, 0, n - 1);
      }
      // slot[w][s] = t+1 exactly when slotOf[w][t] = s
      m.inverseChanneling(slot[w], slotOf[w], 1, 0).post();
    }

    // every team plays at most twice in the same period over the tournament
    for (int t = 1; t <= n; t++) {
      for (int p = 0; p < periods; p++) {
        IntVar[] column = new IntVar[2 * weeks];
        for (int w = 0; w < weeks; w++) {
          column[2 * w] = home[w][p];
          column[2 * w + 1] = away[w][p];
        }
        // number of times team t appears in period p, at most 2
        IntVar times = m.intVar(0, 2);
        m.count(t, column, times).post();
      }
    }

    // every team plays every other team once: opp[t][w] is the opponent of team t in week w,
    // the team in the partner slot (slot 2p with 2p+1, and the reverse)
    IntVar[][] opp = new IntVar[n][weeks];
    for (int t = 0; t < n; t++) {
      for (int w = 0; w < weeks; w++) {
        IntVar s = slotOf[w][t];
        IntVar partner = s.div(2).mul(2).add(1).sub(s.mod(2)).intVar();
        opp[t][w] = m.intVar(1, n);
        m.element(opp[t][w], slot[w], partner, 0).post();
      }
      // the n-1 opponents of team t are all different, so they are exactly the other teams
      m.allDifferent(opp[t], "AC").post();
    }

    // symmetry breaking: relabelling the teams lets week 1 be the fixed round 1 v 2, 3 v 4, ...
    for (int p = 0; p < periods; p++) {
      m.arithm(home[0][p], "=", 2 * p + 1).post();
      m.arithm(away[0][p], "=", 2 * p + 2).post();
    }

    // search: branch on the slots of the schedule, most constrained slot first, with restarts
    IntVar[] slots = new IntVar[2 * weeks * periods];
    int k = 0;
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        slots[k++] = home[w][p];
        slots[k++] = away[w][p];
      }
    }

    out.put("home", home);
    out.put("away", away);
  }
}
