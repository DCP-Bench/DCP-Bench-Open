import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// ACC basketball timetable 1997/98: a double round-robin of 9 teams over 18 dates, with
// mirroring, home/away/bye pattern, weekend, rival, constrained-match, opponent-sequence and
// other constraints of the description.
public class Submission {
  // team indices, in the order the description lists them
  static final int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;
  // where values: home, bye, away (as printed in the description)
  static final int HOME = 0, BYE = 1, AWAY = 2;
  // mirroring scheme of the description, as 0-based date pairs (dates are indices d-1)
  static final int[][] MIRROR = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {9, 16}, {10, 17}};

  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_teams");
    int days = inst.getInt("n_days");
    int np = MIRROR.length;

    // pairOf[d]: the mirror pair that date d belongs to
    int[] pairOf = new int[days];
    for (int p = 0; p < np; p++) {
      pairOf[MIRROR[p][0]] = p;
      pairOf[MIRROR[p][1]] = p;
    }

    // opp[p][i]: opponent of team i in mirror pair p, on both of its dates (i itself is a bye)
    IntVar[][] opp = new IntVar[np][n];
    for (int p = 0; p < np; p++) for (int i = 0; i < n; i++) opp[p][i] = m.intVar("opp_" + p + "_" + i, 0, n - 1);
    // where[d][i]: HOME, BYE or AWAY of team i on date d
    IntVar[][] where = new IntVar[days][n];
    for (int d = 0; d < days; d++) for (int i = 0; i < n; i++) where[d][i] = m.intVar("where_" + d + "_" + i, HOME, AWAY);

    // a match is one game: x_i = j <=> x_j = i within a date pair, a fixed point is a bye
    for (int p = 0; p < np; p++) m.inverseChanneling(opp[p], opp[p]).post();

    // double round robin: each team meets each other team once over the nine pairs, and its own
    // index once (its bye)
    for (int i = 0; i < n; i++) {
      IntVar[] column = new IntVar[np];
      for (int p = 0; p < np; p++) column[p] = opp[p][i];
      m.allDifferent(column, "AC").post();
    }

    // bye and opponent: a team has a bye exactly when its opponent is itself, and an opponent is
    // at home for one team and away for the other
    for (int d = 0; d < days; d++) {
      int p = pairOf[d];
      for (int i = 0; i < n; i++) {
        Tuples t = new Tuples(true);
        t.add(new int[]{i, BYE});
        for (int j = 0; j < n; j++) {
          if (j == i) continue;
          t.add(new int[]{j, HOME});
          t.add(new int[]{j, AWAY});
        }
        m.table(new IntVar[]{opp[p][i], where[d][i]}, t).post();
        IntVar partner = m.intVar(HOME, AWAY);
        m.element(partner, where[d], opp[p][i], 0).post();
        m.arithm(where[d][i], "+", partner, "=", 2).post();
      }
      // each date: four home games, four away games and one bye
      m.count(HOME, where[d], m.intVar(4)).post();
      m.count(AWAY, where[d], m.intVar(4)).post();
      m.count(BYE, where[d], m.intVar(1)).post();
    }

    // each meeting is once at home and once away: in a mirror pair the two dates swap home and away
    for (int[] pair : MIRROR) {
      for (int i = 0; i < n; i++) m.arithm(where[pair[0]][i], "+", where[pair[1]][i], "=", 2).post();
    }

    for (int i = 0; i < n; i++) {
      // 2. no two final aways: no team is away on both of the last two dates
      forbidAll(m, new IntVar[]{where[days - 2][i], where[days - 1][i]}, new int[]{AWAY});

      // 3. home/away/bye patterns over runs of consecutive dates
      for (int d = 0; d + 3 <= days; d++) {
        forbidAll(m, new IntVar[]{where[d][i], where[d + 1][i], where[d + 2][i]}, new int[]{AWAY});
        forbidAll(m, new IntVar[]{where[d][i], where[d + 1][i], where[d + 2][i]}, new int[]{HOME});
      }
      for (int d = 0; d + 4 <= days; d++) {
        forbidAll(m, new IntVar[]{where[d][i], where[d + 1][i], where[d + 2][i], where[d + 3][i]},
            new int[]{AWAY, BYE});
      }
      for (int d = 0; d + 5 <= days; d++) {
        forbidAll(m, new IntVar[]{where[d][i], where[d + 1][i], where[d + 2][i], where[d + 3][i], where[d + 4][i]},
            new int[]{HOME, BYE});
      }
    }

    // 4. weekends are the even dates 2, 4, ..., 18 (indices 1, 3, ..., 17): each team plays four
    // at home, four away and has one bye
    int[] weekend = range(1, days, 2);
    for (int i = 0; i < n; i++) {
      IntVar[] w = column(where, i, weekend);
      m.count(HOME, w, m.intVar(4)).post();
      m.count(AWAY, w, m.intVar(4)).post();
      m.count(BYE, w, m.intVar(1)).post();
    }

    // 5. first five weekends (dates 2, 4, 6, 8, 10): home or bye on at least two of them
    int[] firstFive = {1, 3, 5, 7, 9};
    for (int i = 0; i < n; i++) {
      IntVar[] homeOrBye = new IntVar[firstFive.length];
      for (int k = 0; k < firstFive.length; k++) homeOrBye[k] = m.isLeq(where[firstFive[k]][i], 1);
      m.sum(homeOrBye, ">=", 2).post();
    }

    // 6. rival matches on the last date: every team except FSU plays FSU, has a bye, or plays its
    // rival. Rivals: Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA
    int[] rival = new int[n];
    rival[CLEM] = GT; rival[GT] = CLEM;
    rival[DUKE] = UNC; rival[UNC] = DUKE;
    rival[UMD] = UVA; rival[UVA] = UMD;
    rival[NCST] = WAKE; rival[WAKE] = NCST;
    int last = days - 1;
    for (int i = 0; i < n; i++) {
      if (i == FSU) continue;
      Tuples t = new Tuples(true);
      t.add(new int[]{FSU});
      t.add(new int[]{i});
      t.add(new int[]{rival[i]});
      m.table(new IntVar[]{opp[pairOf[last]][i]}, t).post();
    }

    // 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once in dates 11 to 18
    // (indices 10..17)
    int[] late = range(10, days, 1);
    int[][] required = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
    for (int[] r : required) {
      IntVar[] met = new IntVar[late.length];
      for (int k = 0; k < late.length; k++) met[k] = m.isEq(opp[pairOf[late[k]]][r[0]], r[1]);
      m.sum(met, ">=", 1).post();
    }

    // 8. opponent sequences
    for (int i = 0; i < n; i++) {
      // no two consecutive dates away against UNC and Duke (either order)
      for (int d = 0; d + 1 < days; d++) {
        Tuples t = new Tuples(false);
        t.add(new int[]{UNC, AWAY, DUKE, AWAY});
        t.add(new int[]{DUKE, AWAY, UNC, AWAY});
        m.table(new IntVar[]{opp[pairOf[d]][i], where[d][i], opp[pairOf[d + 1]][i], where[d + 1][i]}, t).post();
      }
      // no three consecutive dates against UNC, Duke and Wake, in any order
      int[] set = {UNC, DUKE, WAKE};
      for (int d = 0; d + 2 < days; d++) {
        Tuples t = new Tuples(false);
        for (int a : set) for (int b : set) for (int c : set) {
          if (a != b && b != c && a != c) t.add(new int[]{a, b, c});
        }
        m.table(new IntVar[]{opp[pairOf[d]][i], opp[pairOf[d + 1]][i], opp[pairOf[d + 2]][i]}, t).post();
      }
    }

    // 9. other constraints, all on the dates named in the description
    m.arithm(opp[pairOf[10]][UNC], "=", DUKE).post();          // UNC plays Duke on date 11 ...
    m.arithm(opp[pairOf[17]][UNC], "=", DUKE).post();          // ... and on the last date 18
    m.arithm(opp[pairOf[1]][UNC], "=", CLEM).post();           // UNC plays Clem on date 2
    m.arithm(opp[pairOf[15]][DUKE], "=", DUKE).post();         // Duke has a bye on date 16
    m.arithm(where[16][WAKE], "!=", HOME).post();              // Wake does not play home on date 17
    m.arithm(opp[pairOf[0]][WAKE], "=", WAKE).post();          // Wake has a bye on date 1
    for (int i : new int[]{CLEM, DUKE, UMD, WAKE}) {
      m.arithm(where[last][i], "!=", AWAY).post();             // no away game on the last date
    }
    for (int i : new int[]{CLEM, FSU, GT, WAKE}) {
      m.arithm(where[0][i], "!=", AWAY).post();                // no away game on the first date
    }
    m.arithm(opp[pairOf[last]][FSU], "!=", FSU).post();        // FSU has no bye on the last date
    m.arithm(opp[pairOf[last]][NCST], "!=", NCST).post();      // NCSt has no bye on the last date
    m.arithm(opp[pairOf[0]][UNC], "!=", UNC).post();           // UNC has no bye on the first date

    // search: the opponents fix the structure, then the home/away/bye pattern
    IntVar[] flatOpp = new IntVar[np * n];
    for (int p = 0; p < np; p++) for (int i = 0; i < n; i++) flatOpp[p * n + i] = opp[p][i];
    IntVar[] flatWhere = new IntVar[days * n];
    for (int d = 0; d < days; d++) for (int i = 0; i < n; i++) flatWhere[d * n + i] = where[d][i];
    m.getSolver().setSearch(Search.domOverWDegSearch(flatOpp), Search.domOverWDegSearch(flatWhere));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    // config[d][i]: opponent of team i on date d (i itself on a bye); where[d][i] as above
    IntVar[][] config = new IntVar[days][n];
    for (int d = 0; d < days; d++) for (int i = 0; i < n; i++) config[d][i] = opp[pairOf[d]][i];
    out.put("config", config);
    out.put("where", where);
  }

  // every tuple over the given values for these variables is forbidden
  static void forbidAll(Model m, IntVar[] vars, int[] values) {
    int k = vars.length;
    int total = 1;
    for (int p = 0; p < k; p++) total *= values.length;
    Tuples t = new Tuples(false);
    for (int code = 0; code < total; code++) {
      int[] row = new int[k];
      int c = code;
      for (int p = 0; p < k; p++) {
        row[p] = values[c % values.length];
        c /= values.length;
      }
      t.add(row);
    }
    m.table(vars, t).post();
  }

  static int[] range(int from, int to, int step) {
    int len = 0;
    for (int x = from; x < to; x += step) len++;
    int[] r = new int[len];
    for (int k = 0; k < len; k++) r[k] = from + k * step;
    return r;
  }

  static IntVar[] column(IntVar[][] a, int i, int[] days) {
    IntVar[] r = new IntVar[days.length];
    for (int k = 0; k < days.length; k++) r[k] = a[days[k]][i];
    return r;
  }
}
