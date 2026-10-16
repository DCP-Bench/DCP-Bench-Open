import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Diagnostic 5: per week a perfect matching of teams (y), slots as 0/1 home and away choices,
// clauses linking a slot to the matching, pair meetings as linear sums of matching variables.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_teams");
    int weeks = n - 1;
    int periods = n / 2;

    // meet[w][t][u] for t < u: teams t and u play each other in week w
    CPBoolVar[][][] meet = new CPBoolVar[weeks][n + 1][n + 1];
    for (int w = 0; w < weeks; w++) {
      for (int t = 1; t <= n; t++) {
        for (int u = t + 1; u <= n; u++) {
          meet[w][t][u] = not(m.boolVar());
        }
      }
    }

    CPBoolVar[][][] atHome = new CPBoolVar[weeks][periods][n + 1];
    CPBoolVar[][][] atAway = new CPBoolVar[weeks][periods][n + 1];
    CPIntVar[][] home = new CPIntVar[weeks][periods];
    CPIntVar[][] away = new CPIntVar[weeks][periods];
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        CPIntVar[] hs = new CPIntVar[n];
        CPIntVar[] as = new CPIntVar[n];
        CPBoolVar[] hb = new CPBoolVar[n];
        CPBoolVar[] ab = new CPBoolVar[n];
        for (int t = 1; t <= n; t++) {
          atHome[w][p][t] = m.boolVar();
          atAway[w][p][t] = m.boolVar();
          hb[t - 1] = atHome[w][p][t];
          ab[t - 1] = atAway[w][p][t];
          hs[t - 1] = mul(atHome[w][p][t], t);
          as[t - 1] = mul(atAway[w][p][t], t);
        }
        m.cp().post(eq(sum(hb), 1));
        m.cp().post(eq(sum(ab), 1));
        home[w][p] = sum(hs);
        away[w][p] = sum(as);
      }
    }

    // every team plays once a week, against exactly one opponent
    for (int w = 0; w < weeks; w++) {
      for (int t = 1; t <= n; t++) {
        CPBoolVar[] opp = new CPBoolVar[n - 1];
        int k = 0;
        for (int u = 1; u <= n; u++) {
          if (u == t) continue;
          opp[k++] = t < u ? meet[w][t][u] : meet[w][u][t];
        }
        m.cp().post(eq(sum(opp), 1));
      }
    }

    // every team plays once a week: it holds exactly one of the slots of the week
    for (int w = 0; w < weeks; w++) {
      for (int t = 1; t <= n; t++) {
        CPBoolVar[] slots = new CPBoolVar[2 * periods];
        int k = 0;
        for (int p = 0; p < periods; p++) {
          slots[k++] = atHome[w][p][t];
          slots[k++] = atAway[w][p][t];
        }
        m.cp().post(eq(sum(slots), 1));
      }
    }

    // every team plays every other team once: each pair meets in exactly one week
    for (int t = 1; t <= n; t++) {
      for (int u = t + 1; u <= n; u++) {
        CPBoolVar[] weeksMeet = new CPBoolVar[weeks];
        for (int w = 0; w < weeks; w++) weeksMeet[w] = meet[w][t][u];
        m.cp().post(eq(sum(weeksMeet), 1));
      }
    }
    // the opponents of a team over the weeks are all different
    for (int t = 1; t <= n; t++) {
      CPIntVar[] opponents = new CPIntVar[weeks];
      for (int w = 0; w < weeks; w++) {
        CPIntVar[] terms = new CPIntVar[n - 1];
        int k = 0;
        for (int u = 1; u <= n; u++) {
          if (u == t) continue;
          CPBoolVar mt = t < u ? meet[w][t][u] : meet[w][u][t];
          terms[k++] = mul(mt, u);
        }
        opponents[w] = sum(terms);
      }
      m.cp().post(allDifferent(opponents));
    }

    // the slots: a period's home and away teams play each other that week
    for (int w = 0; w < weeks; w++) {
      for (int p = 0; p < periods; p++) {
        for (int t = 1; t <= n; t++) {
          for (int u = 1; u <= n; u++) {
            if (u == t) continue;
            CPBoolVar mt = t < u ? meet[w][t][u] : meet[w][u][t];
            m.cp().post(or(new CPBoolVar[] {not(atHome[w][p][t]), not(atAway[w][p][u]), mt}));
          }
        }
      }
    }

    // every team plays at most twice in the same period over the tournament, and at least once
    for (int t = 1; t <= n; t++) {
      for (int p = 0; p < periods; p++) {
        CPBoolVar[] plays = new CPBoolVar[2 * weeks];
        int k = 0;
        for (int w = 0; w < weeks; w++) {
          plays[k++] = atHome[w][p][t];
          plays[k++] = atAway[w][p][t];
        }
        m.cp().post(le(sum(plays), 2));
        m.cp().post(ge(sum(plays), 1));
      }
    }

    out.put("home", home);
    out.put("away", away);
  }
}
