import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// N-puzzle: a list of N_STEPS boards, the first is puzzle_start and the last is puzzle_end.
// Each board is an n x n grid (n taken from the instance) holding the tiles 0..n*n-1,
// where 0 is the empty square and every value appears exactly once.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int steps = inst.getInt("N_STEPS");
    int[][] start = inst.getIntMatrix("puzzle_start");
    int[][] end = inst.getIntMatrix("puzzle_end");
    int n = start.length;
    int cells = n * n;

    // one variable per square of each board
    CPIntVar[][] s = new CPIntVar[steps][cells];
    for (int t = 0; t < steps; t++) {
      s[t] = m.intVarArray(cells, 0, cells - 1);
    }

    // every board holds each tile exactly once
    for (int t = 0; t < steps; t++) {
      m.cp().post(allDifferent(s[t]));
    }

    // the first board is the start state
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        m.cp().post(eq(s[0][i * n + j], start[i][j]));
      }
    }

    // the last board is the end state
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        m.cp().post(eq(s[steps - 1][i * n + j], end[i][j]));
      }
    }

    // the empty square is the square holding 0
    CPBoolVar[][] blank = new CPBoolVar[steps][cells];
    for (int t = 0; t < steps; t++) {
      for (int k = 0; k < cells; k++) {
        blank[t][k] = isEq(s[t][k], 0);
      }
    }

    // a tile slides into the empty square from a neighbouring square: the empty square
    // moves to a square next to its previous one, and no other square is changed
    for (int t = 0; t + 1 < steps; t++) {
      // the empty square moves only to a neighbour, so it never stays or jumps
      for (int c = 0; c < cells; c++) {
        for (int d = 0; d < cells; d++) {
          if (manhattan(n, c, d) != 1) {
            m.cp().post(or(new CPBoolVar[] {not(blank[t][c]), not(blank[t + 1][d])}));
          }
        }
      }
      // every square that is neither empty before nor after the move keeps its tile
      for (int k = 0; k < cells; k++) {
        m.cp().post(or(new CPBoolVar[] {blank[t][k], blank[t + 1][k], isEq(s[t][k], s[t + 1][k])}));
      }
    }

    // freezing is not allowed: each step changes the board (implied by the moves above)

    CPIntVar[][][] boards = new CPIntVar[steps][n][n];
    for (int t = 0; t < steps; t++) {
      for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
          boards[t][i][j] = s[t][i * n + j];
        }
      }
    }
    out.put("steps", boards);
  }

  // Manhattan distance between squares c and d of an n x n grid
  private static int manhattan(int n, int c, int d) {
    return Math.abs(c / n - d / n) + Math.abs(c % n - d % n);
  }
}
