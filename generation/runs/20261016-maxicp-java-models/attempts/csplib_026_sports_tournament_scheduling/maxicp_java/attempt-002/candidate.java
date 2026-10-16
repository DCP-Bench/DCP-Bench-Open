import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Sports tournament scheduling: n teams play over n-1 weeks. Each week has n/2 periods, and each
// period has a home slot and an away slot. The teams are numbered 1 to n.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_teams");
    int weeks = n - 1;
    int periods = n / 2;

    // hm[w][p][t]: team t plays at home in period p of week w; aw[w][p][t]: team t plays away there
    CPBoolVar[][][] hm = new CPBoolVar[weeks][periods][n + 1];
    CPBoolVar[][][] aw = new CPBoolVar[weeks][periods][n + 1];
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        for (int t = 1; t <= n; t++) {
          hm[w][p][t] = m.boolVar();
          aw[w][p][t] = m.boolVar();
        }
      }
    }

    // each period has one team at home and one team away
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        CPBoolVar[] h = new CPBoolVar[n];
        CPBoolVar[] a = new CPBoolVar[n];
        for (int t = 1; t <= n; t++) {
          h[t - 1] = hm[w][p][t];
          a[t - 1] = aw[w][p][t];
        }
        m.cp().post(eq(sum(h), 1));
        m.cp().post(eq(sum(a), 1));
      }
    }

    // every team plays once a week: it holds exactly one of the slots of the week
    for (int w = 0; w < weeks; w++) {
      for (int t = 1; t <= n; t++) {
        CPBoolVar[] slots = new CPBoolVar[2 * periods];
        int k = 0;
        for (int p = 0; p < periods; p++) {
          slots[k++] = hm[w][p][t];
          slots[k++] = aw[w][p][t];
        }
        m.cp().post(eq(sum(slots), 1));
      }
    }

    // every team plays at most twice in the same period over the tournament.
    // Implied: a team plays n-1 games in n/2 periods, so it plays at least once in each period.
    for (int t = 1; t <= n; t++) {
      for (int p = 0; p < periods; p++) {
        CPBoolVar[] plays = new CPBoolVar[2 * weeks];
        int k = 0;
        for (int w = 0; w < weeks; w++) {
          plays[k++] = hm[w][p][t];
          plays[k++] = aw[w][p][t];
        }
        m.cp().post(le(sum(plays), 2));
        m.cp().post(ge(sum(plays), 1));
      }
    }

    // every team plays every other team: the pair meets in exactly one period of one week.
    // met[w][p][t][u] (t < u) is true when t and u are the two teams of period p in week w.
    CPBoolVar[][][][] met = new CPBoolVar[weeks][periods][n + 1][n + 1];
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        for (int t = 1; t <= n; t++) {
          for (int u = t + 1; u <= n; u++) {
            CPBoolVar x = makeBoolVar(m.cp());
            met[w][p][t][u] = x;
            m.cp().post(or(new CPBoolVar[] {not(x), hm[w][p][t], aw[w][p][t]}));
            m.cp().post(or(new CPBoolVar[] {not(x), hm[w][p][u], aw[w][p][u]}));
            m.cp().post(or(new CPBoolVar[] {not(hm[w][p][t]), not(aw[w][p][u]), x}));
            m.cp().post(or(new CPBoolVar[] {not(aw[w][p][t]), not(hm[w][p][u]), x}));
          }
        }
      }
    }
    for (int t = 1; t <= n; t++) {
      for (int u = t + 1; u <= n; u++) {
        CPBoolVar[] together = new CPBoolVar[weeks * periods];
        int k = 0;
        for (int w = 0; w < weeks; w++) {
          for (int p = 0; p < periods; p++) {
            together[k++] = met[w][p][t][u];
          }
        }
        m.cp().post(eq(sum(together), 1));
      }
    }

    // home[w][p] and away[w][p]: the team numbers in the home and the away slot
    CPIntVar[][] home = new CPIntVar[weeks][periods];
    CPIntVar[][] away = new CPIntVar[weeks][periods];
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        CPIntVar[] hs = new CPIntVar[n];
        CPIntVar[] as = new CPIntVar[n];
        for (int t = 1; t <= n; t++) {
          hs[t - 1] = mul(hm[w][p][t], t);
          as[t - 1] = mul(aw[w][p][t], t);
        }
        home[w][p] = sum(hs);
        away[w][p] = sum(as);
      }
    }

    out.put("home", home);
    out.put("away", away);
  }
}
