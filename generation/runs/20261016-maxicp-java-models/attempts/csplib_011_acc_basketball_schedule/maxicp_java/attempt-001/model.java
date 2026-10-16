import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// 1997/98 Atlantic Coast Conference basketball timetable: a double round-robin of the nine teams over
// the 18 dates, with mirroring, home/away/bye patterns, weekend and rival rules, and fixed match-ups.
// config[d][i] is the team that team i plays on date d; it is team i itself when team i has a bye.
// where[d][i] is 0 when team i plays at home, 1 when it has a bye, 2 when it plays away.
// Teams are indexed in the order of the statement: 0 Clemson, 1 Duke, 2 FSU, 3 Georgia Tech,
// 4 Maryland, 5 UNC, 6 NC State, 7 Virginia, 8 Wake Forest. Dates and weekends are 0-based here:
// date d+1 of the statement is index d, so the first weekend is index 1 and the last date is index 17.
//
// The decisions are 0/1 variables: home[d][i][j] is 1 when team i plays at home against team j on
// date d, away[d][i][j] when it plays away at j, and bye[d][i] when team i has a bye. config and
// where are sums of these.
public class Submission {
  static final int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;
  static final int HOME = 0, BYE = 1, AWAY = 2;

  static int T, D;
  static CPBoolVar[][][] home, away;
  static CPBoolVar[][] bye;

  public static void build(Instance inst, Model m, Outputs out) {
    T = inst.getInt("n_teams");
    D = inst.getInt("n_days");
    CPSolver cp = m.cp();

    home = new CPBoolVar[D][T][T];
    away = new CPBoolVar[D][T][T];
    bye = new CPBoolVar[D][T];
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++) {
        bye[d][i] = m.boolVar();
        for (int j = 0; j < T; j++)
          if (i != j) home[d][i][j] = m.boolVar();
      }
    // team i is away against j on a date exactly when j is at home against i that date
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++)
        for (int j = 0; j < T; j++)
          if (i != j) away[d][i][j] = home[d][j][i];

    // each team plays exactly one opponent, or has a bye, on each date
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++) {
        List<CPIntVar> xs = new ArrayList<>();
        xs.add(bye[d][i]);
        for (int j = 0; j < T; j++)
          if (i != j) { xs.add(home[d][i][j]); xs.add(away[d][i][j]); }
        cp.post(sum(ints(xs), 1));
      }

    // double round robin: each team plays each other team once at home and once away
    for (int i = 0; i < T; i++)
      for (int j = 0; j < T; j++) {
        if (i == j) continue;
        List<CPIntVar> h = new ArrayList<>();
        List<CPIntVar> a = new ArrayList<>();
        for (int d = 0; d < D; d++) { h.add(home[d][i][j]); a.add(away[d][i][j]); }
        cp.post(sum(ints(h), 1));
        cp.post(sum(ints(a), 1));
      }

    // each team has two byes in the 18 dates
    for (int i = 0; i < T; i++) {
      List<CPIntVar> b = new ArrayList<>();
      for (int d = 0; d < D; d++) b.add(bye[d][i]);
      cp.post(sum(ints(b), 2));
    }

    // Mirroring: the dates (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18)
    // pair up, and each team plays the same opponent on both dates of a pair (a bye on both)
    int[][] mirror = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {9, 16}, {10, 17}};
    for (int[] pair : mirror)
      for (int i = 0; i < T; i++) {
        cp.post(eq(bye[pair[0]][i], bye[pair[1]][i]));
        for (int j = 0; j < T; j++)
          if (i != j) cp.post(eq(playsOn(pair[0], i, j), playsOn(pair[1], i, j)));
      }

    // Weekend Pattern: the weekends are the even-numbered dates (indices 1, 3, ..., 17); each team plays
    // four weekends at home, four away, and has one bye
    for (int i = 0; i < T; i++) {
      List<CPIntVar> h = new ArrayList<>();
      List<CPIntVar> a = new ArrayList<>();
      List<CPIntVar> b = new ArrayList<>();
      for (int d = 1; d < D; d += 2) {
        b.add(bye[d][i]);
        h.addAll(homeTerms(d, i));
        a.addAll(awayTerms(d, i));
      }
      cp.post(sum(ints(h), 4));
      cp.post(sum(ints(a), 4));
      cp.post(sum(ints(b), 1));
    }

    // No Two Final Aways: no team plays away on both of the last two dates
    for (int i = 0; i < T; i++)
      {
        List<CPIntVar> xs = new ArrayList<>(awayTerms(D - 2, i));
        xs.addAll(awayTerms(D - 1, i));
        cp.post(le(sum(ints(xs)), 1));
      }

    // First Weekends: each team has home matches or byes on at least two of the first five weekends
    // (indices 1, 3, 5, 7, 9)
    for (int i = 0; i < T; i++) {
      List<CPIntVar> xs = new ArrayList<>();
      for (int d = 1; d <= 9; d += 2) xs.addAll(homeOrByeTerms(d, i));
      cp.post(ge(sum(ints(xs)), 2));
    }

    // Home/Away/Bye Pattern: no team has more than two away matches in a row, and no team has more than
    // two home matches in a row
    for (int i = 0; i < T; i++)
      for (int d = 0; d + 2 < D; d++) {
        List<CPIntVar> aw = new ArrayList<>();
        List<CPIntVar> hm = new ArrayList<>();
        for (int k = 0; k < 3; k++) { aw.addAll(awayTerms(d + k, i)); hm.addAll(homeTerms(d + k, i)); }
        cp.post(le(sum(ints(aw)), 2));
        cp.post(le(sum(ints(hm)), 2));
      }

    // Home/Away/Bye Pattern: no team has more than three away matches or byes in a row, and no team has
    // more than four home matches or byes in a row
    for (int i = 0; i < T; i++) {
      for (int d = 0; d + 3 < D; d++) {
        List<CPIntVar> xs = new ArrayList<>();
        for (int k = 0; k < 4; k++) xs.addAll(awayOrByeTerms(d + k, i));
        cp.post(le(sum(ints(xs)), 3));
      }
      for (int d = 0; d + 4 < D; d++) {
        List<CPIntVar> xs = new ArrayList<>();
        for (int k = 0; k < 5; k++) xs.addAll(homeOrByeTerms(d + k, i));
        cp.post(le(sum(ints(xs)), 4));
      }
    }

    // Rival Matches: on the last date, every team except FSU plays its rival, unless it plays against FSU
    // or has a bye (rivals: Duke-UNC, Clemson-Georgia Tech, NC State-Wake Forest, Maryland-Virginia)
    int[] rival = new int[T];
    Arrays.fill(rival, -1);
    rival[CLEM] = GT; rival[GT] = CLEM;
    rival[DUKE] = UNC; rival[UNC] = DUKE;
    rival[NCST] = WAKE; rival[WAKE] = NCST;
    rival[UMD] = UVA; rival[UVA] = UMD;
    for (int i = 0; i < T; i++) {
      if (i == FSU) continue;
      cp.post(ge(sum(ints(List.of(bye[D - 1][i], playsOn(D - 1, i, rival[i]), playsOn(D - 1, i, FSU)))), 1));
    }

    // Constrained Matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke must occur at least once in dates 11 to 18
    int[][] constrained = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
    for (int[] pair : constrained) {
      List<CPIntVar> xs = new ArrayList<>();
      for (int d = 10; d < D; d++) xs.add(playsOn(d, pair[0], pair[1]));
      cp.post(ge(sum(ints(xs)), 1));
    }

    // Opponent Sequence: no team plays in two consecutive dates away against UNC and Duke (in either order)
    for (int i = 0; i < T; i++)
      for (int d = 0; d + 1 < D; d++) {
        if (i != UNC && i != DUKE) {
          cp.post(le(sum(ints(List.of(away[d][i][UNC], away[d + 1][i][DUKE]))), 1));
          cp.post(le(sum(ints(List.of(away[d][i][DUKE], away[d + 1][i][UNC]))), 1));
        }
      }

    // Opponent Sequence: no team plays in three consecutive dates against UNC, Duke and Wake, whether home or away
    int[][] orders = {{UNC, DUKE, WAKE}, {UNC, WAKE, DUKE}, {DUKE, UNC, WAKE},
                      {DUKE, WAKE, UNC}, {WAKE, UNC, DUKE}, {WAKE, DUKE, UNC}};
    for (int i = 0; i < T; i++)
      for (int d = 0; d + 2 < D; d++)
        for (int[] o : orders) {
          List<CPIntVar> xs = new ArrayList<>();
          for (int k = 0; k < 3; k++) if (o[k] != i) xs.add(playsOn(d + k, i, o[k]));
          if (xs.size() == 3) cp.post(le(sum(ints(xs)), 2));
        }

    // Other Constraints: UNC plays its rival Duke in the last date and in date 11
    cp.post(eq(playsOn(D - 1, UNC, DUKE), 1));
    cp.post(eq(playsOn(10, UNC, DUKE), 1));
    // UNC plays Clemson in the second date
    cp.post(eq(playsOn(1, UNC, CLEM), 1));
    // Duke has a bye in date 16
    cp.post(eq(bye[15][DUKE], 1));
    // Wake Forest does not play at home in date 17
    cp.post(sum(ints(homeTerms(16, WAKE)), 0));
    // Wake Forest has a bye in the first date
    cp.post(eq(bye[0][WAKE], 1));
    // Clemson, Duke, Maryland and Wake Forest do not play away in the last date
    for (int t : new int[] {CLEM, DUKE, UMD, WAKE}) cp.post(sum(ints(awayTerms(D - 1, t)), 0));
    // Clemson, FSU, Georgia Tech and Wake Forest do not play away in the first date
    for (int t : new int[] {CLEM, FSU, GT, WAKE}) cp.post(sum(ints(awayTerms(0, t)), 0));
    // Neither FSU nor NC State has a bye in the last date
    cp.post(eq(bye[D - 1][FSU], 0));
    cp.post(eq(bye[D - 1][NCST], 0));
    // UNC does not have a bye in the first date
    cp.post(eq(bye[0][UNC], 0));

    CPIntVar[][] config = new CPIntVar[D][T];
    CPIntVar[][] where = new CPIntVar[D][T];
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++) {
        List<CPIntVar> c = new ArrayList<>();
        List<CPIntVar> w = new ArrayList<>();
        for (int j = 0; j < T; j++)
          if (i != j) {
            c.add(mul(home[d][i][j], j));
            c.add(mul(away[d][i][j], j));
            w.add(mul(away[d][i][j], AWAY));
          }
        if (i != 0) c.add(mul(bye[d][i], i));
        w.add(bye[d][i]);
        config[d][i] = sum(ints(c));
        where[d][i] = sum(ints(w));
      }
    out.put("config", config);
    out.put("where", where);
  }

  // 1 when team i plays team j on date d, at either venue
  static CPIntVar playsOn(int d, int i, int j) {
    return sum(new CPIntVar[] {home[d][i][j], away[d][i][j]});
  }

  // the 0/1 terms that are 1 when team i plays at home on date d (at most one of them)
  static List<CPIntVar> homeTerms(int d, int i) {
    List<CPIntVar> xs = new ArrayList<>();
    for (int j = 0; j < T; j++) if (i != j) xs.add(home[d][i][j]);
    return xs;
  }

  // the 0/1 terms that are 1 when team i plays away on date d (at most one of them)
  static List<CPIntVar> awayTerms(int d, int i) {
    List<CPIntVar> xs = new ArrayList<>();
    for (int j = 0; j < T; j++) if (i != j) xs.add(away[d][i][j]);
    return xs;
  }

  // home match or bye on date d: at most one of these terms is 1, since a bye is no match
  static List<CPIntVar> homeOrByeTerms(int d, int i) {
    List<CPIntVar> xs = homeTerms(d, i);
    xs.add(bye[d][i]);
    return xs;
  }

  // away match or bye on date d: at most one of these terms is 1
  static List<CPIntVar> awayOrByeTerms(int d, int i) {
    List<CPIntVar> xs = awayTerms(d, i);
    xs.add(bye[d][i]);
    return xs;
  }

  static CPIntVar[] ints(List<? extends CPIntVar> xs) {
    return xs.toArray(new CPIntVar[0]);
  }
}
