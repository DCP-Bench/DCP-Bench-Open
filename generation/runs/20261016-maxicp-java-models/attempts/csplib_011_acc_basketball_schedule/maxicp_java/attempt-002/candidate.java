import java.util.ArrayList;
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
// The decisions are the opponent config[d][i] (one integer per team and date) and the venue where[d][i].
// Reified Booleans state the meetings, home matches, away matches and byes; they are views over the decisions.
public class Submission {
  static final int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;
  static final int HOME = 0, BYE = 1, AWAY = 2;

  static int T, D;
  static CPIntVar[][] config, where;
  static CPBoolVar[][][] meet;            // meet[d][i][j]: team i plays team j on date d, at either venue
  static CPBoolVar[][] isHome, isAway, isBye;

  public static void build(Instance inst, Model m, Outputs out) {
    T = inst.getInt("n_teams");
    D = inst.getInt("n_days");
    CPSolver cp = m.cp();

    config = new CPIntVar[D][T];
    where = new CPIntVar[D][T];
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++) {
        config[d][i] = m.intVar(0, T - 1);
        where[d][i] = makeIntVar(cp, HOME, AWAY);
      }

    meet = new CPBoolVar[D][T][T];
    isHome = new CPBoolVar[D][T];
    isAway = new CPBoolVar[D][T];
    isBye = new CPBoolVar[D][T];
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++) {
        isHome[d][i] = isEq(where[d][i], HOME);
        isAway[d][i] = isEq(where[d][i], AWAY);
        isBye[d][i] = isEq(where[d][i], BYE);
        for (int j = 0; j < T; j++)
          if (i != j) meet[d][i][j] = isEq(config[d][i], j);
      }

    // a bye is the only case where a team is its own opponent, and the opponent is a bye exactly when the venue says so
    for (int d = 0; d < D; d++)
      for (int i = 0; i < T; i++) {
        cp.post(eq(isBye[d][i], isEq(config[d][i], i)));
        // the opponent's opponent is the team itself: the match is the same match seen from both sides
        cp.post(eq(element(config[d], config[d][i]), i));
        // a home match for one team is an away match for the other, and a bye is 1 on both sides
        cp.post(eq(sum(element(where[d], config[d][i]), where[d][i]), 2));
      }

    // double round robin: each team plays each other team once at home and once away
    for (int i = 0; i < T; i++)
      for (int j = 0; j < T; j++) {
        if (i == j) continue;
        List<CPIntVar> met = new ArrayList<>();
        List<CPIntVar> hm = new ArrayList<>();
        for (int d = 0; d < D; d++) {
          met.add(meet[d][i][j]);
          hm.add(mul(meet[d][i][j], isHome[d][i]));
        }
        cp.post(eq(sum(ints(met)), 2));
        cp.post(eq(sum(ints(hm)), 1));
      }

    // each team has two byes in the 18 dates
    for (int i = 0; i < T; i++) {
      List<CPIntVar> b = new ArrayList<>();
      for (int d = 0; d < D; d++) b.add(isBye[d][i]);
      cp.post(eq(sum(ints(b)), 2));
    }

    // Mirroring: the dates (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18) are grouped
    // in pairs, and each team gets to play against the same team in both dates of a pair
    int[][] mirror = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {9, 16}, {10, 17}};
    for (int[] pair : mirror)
      for (int i = 0; i < T; i++) cp.post(eq(config[pair[0]][i], config[pair[1]][i]));

    // Each date has four matches, so one team has a bye and four teams play at home (implied by the statement)
    for (int d = 0; d < D; d++) {
      List<CPIntVar> b = new ArrayList<>();
      List<CPIntVar> h = new ArrayList<>();
      for (int i = 0; i < T; i++) {
        b.add(isBye[d][i]);
        h.add(isHome[d][i]);
      }
      cp.post(eq(sum(ints(b)), 1));
      cp.post(eq(sum(ints(h)), 4));
    }

    // Each team plays eight matches at home over the season (implied by the double round robin)
    for (int i = 0; i < T; i++) {
      List<CPIntVar> h = new ArrayList<>();
      for (int d = 0; d < D; d++) h.add(isHome[d][i]);
      cp.post(eq(sum(ints(h)), T - 1));
    }

    // Weekend Pattern: of the weekends, each team plays four at home, four away, and one bye
    // (the weekends are the even-numbered dates, indices 1, 3, ..., 17)
    for (int i = 0; i < T; i++) {
      List<CPIntVar> h = new ArrayList<>();
      List<CPIntVar> a = new ArrayList<>();
      List<CPIntVar> b = new ArrayList<>();
      for (int d = 1; d < D; d += 2) {
        h.add(isHome[d][i]);
        a.add(isAway[d][i]);
        b.add(isBye[d][i]);
      }
      cp.post(eq(sum(ints(h)), 4));
      cp.post(eq(sum(ints(a)), 4));
      cp.post(eq(sum(ints(b)), 1));
    }

    // No Two Final Aways: no team can play away on both last dates
    for (int i = 0; i < T; i++)
      cp.post(le(sum(isAway[D - 2][i], isAway[D - 1][i]), 1));

    // First Weekends: each team must have home matches or byes at least on two of the first five weekends
    // (indices 1, 3, 5, 7, 9)
    for (int i = 0; i < T; i++) {
      List<CPIntVar> xs = new ArrayList<>();
      for (int d = 1; d <= 9; d += 2) {
        xs.add(isHome[d][i]);
        xs.add(isBye[d][i]);
      }
      cp.post(ge(sum(ints(xs)), 2));
    }

    // Home/Away/Bye Pattern: no team may have more than two away matches in a row, and no more than two home
    // matches in a row
    for (int i = 0; i < T; i++)
      for (int d = 0; d + 2 < D; d++) {
        List<CPIntVar> aw = new ArrayList<>();
        List<CPIntVar> hm = new ArrayList<>();
        for (int k = 0; k < 3; k++) {
          aw.add(isAway[d + k][i]);
          hm.add(isHome[d + k][i]);
        }
        cp.post(le(sum(ints(aw)), 2));
        cp.post(le(sum(ints(hm)), 2));
      }

    // Home/Away/Bye Pattern: no team may have more than three away matches or byes in a row, and no more than
    // four home matches or byes in a row
    for (int i = 0; i < T; i++) {
      for (int d = 0; d + 3 < D; d++) {
        List<CPIntVar> xs = new ArrayList<>();
        for (int k = 0; k < 4; k++) {
          xs.add(isAway[d + k][i]);
          xs.add(isBye[d + k][i]);
        }
        cp.post(le(sum(ints(xs)), 3));
      }
      for (int d = 0; d + 4 < D; d++) {
        List<CPIntVar> xs = new ArrayList<>();
        for (int k = 0; k < 5; k++) {
          xs.add(isHome[d + k][i]);
          xs.add(isBye[d + k][i]);
        }
        cp.post(le(sum(ints(xs)), 4));
      }
    }

    // Rival Matches: in the last date, every team except FSU plays against its rival, unless it plays against
    // FSU or has a bye (rivals: Duke-UNC, Clemson-Georgia Tech, NC State-Wake Forest, Maryland-Virginia)
    int[] rival = new int[T];
    rival[CLEM] = GT; rival[GT] = CLEM;
    rival[DUKE] = UNC; rival[UNC] = DUKE;
    rival[NCST] = WAKE; rival[WAKE] = NCST;
    rival[UMD] = UVA; rival[UVA] = UMD;
    rival[FSU] = -1;
    for (int i = 0; i < T; i++) {
      if (i == FSU) continue;
      cp.post(ge(sum(ints(List.of(isBye[D - 1][i], meet[D - 1][i][rival[i]], meet[D - 1][i][FSU]))), 1));
    }

    // Constrained Matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke must occur at least once in dates 11 to 18
    int[][] constrained = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
    for (int[] pair : constrained) {
      List<CPIntVar> xs = new ArrayList<>();
      for (int d = 10; d < D; d++) xs.add(meet[d][pair[0]][pair[1]]);
      cp.post(ge(sum(ints(xs)), 1));
    }

    // Opponent Sequence Constraints: no team plays in two consecutive dates away against UNC and Duke
    // (in either order)
    for (int i = 0; i < T; i++) {
      if (i == UNC || i == DUKE) continue;
      for (int d = 0; d + 1 < D; d++) {
        cp.post(le(sum(mul(meet[d][i][UNC], isAway[d][i]), mul(meet[d + 1][i][DUKE], isAway[d + 1][i])), 1));
        cp.post(le(sum(mul(meet[d][i][DUKE], isAway[d][i]), mul(meet[d + 1][i][UNC], isAway[d + 1][i])), 1));
      }
    }

    // Opponent Sequence Constraints: no team plays in three consecutive dates against UNC, Duke and Wake,
    // independent of home or away
    int[][] orders = {{UNC, DUKE, WAKE}, {UNC, WAKE, DUKE}, {DUKE, UNC, WAKE},
                      {DUKE, WAKE, UNC}, {WAKE, UNC, DUKE}, {WAKE, DUKE, UNC}};
    for (int i = 0; i < T; i++) {
      if (i == UNC || i == DUKE || i == WAKE) continue;
      for (int d = 0; d + 2 < D; d++)
        for (int[] o : orders)
          cp.post(le(sum(ints(List.of(meet[d][i][o[0]], meet[d + 1][i][o[1]], meet[d + 2][i][o[2]]))), 2));
    }

    // Other Constraints: UNC plays its rival Duke in the last date, and in date 11
    cp.post(eq(meet[D - 1][UNC][DUKE], 1));
    cp.post(eq(meet[10][UNC][DUKE], 1));
    // UNC plays Clemson in the second date
    cp.post(eq(meet[1][UNC][CLEM], 1));
    // Duke has a bye in date 16
    cp.post(eq(isBye[15][DUKE], 1));
    // Wake Forest does not play at home in date 17
    cp.post(eq(isHome[16][WAKE], 0));
    // Wake Forest has a bye in the first date
    cp.post(eq(isBye[0][WAKE], 1));
    // Clemson, Duke, Maryland and Wake Forest do not play away in the last date
    for (int t : new int[] {CLEM, DUKE, UMD, WAKE}) cp.post(eq(isAway[D - 1][t], 0));
    // Clemson, FSU, Georgia Tech and Wake Forest do not play away in the first date
    for (int t : new int[] {CLEM, FSU, GT, WAKE}) cp.post(eq(isAway[0][t], 0));
    // Neither FSU nor NC State has a bye in the last date
    cp.post(eq(isBye[D - 1][FSU], 0));
    cp.post(eq(isBye[D - 1][NCST], 0));
    // UNC does not have a bye in the first date
    cp.post(eq(isBye[0][UNC], 0));

    out.put("config", config);
    out.put("where", where);
  }

  static CPIntVar[] ints(List<? extends CPIntVar> xs) {
    return xs.toArray(new CPIntVar[0]);
  }
}
