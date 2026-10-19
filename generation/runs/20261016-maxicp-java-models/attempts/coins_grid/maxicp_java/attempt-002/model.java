import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

// Coins on an n by n grid. In each row exactly c coins must be placed, and in
// each column exactly c coins must be placed. At most one coin per cell.
// The sum of the quadratic horizontal distance from the main diagonal of all
// cells containing a coin must be as small as possible. The distance of cell
// (i, j) is i - j, so its cost is (i - j) squared.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int c = inst.getInt("c");

    // a coin is placed in a cell (1) or not (0)
    CPIntVar[][] x = new CPIntVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        x[i][j] = m.intVar(0, 1);
      }
    }

    // in each row exactly c coins must be placed
    for (int i = 0; i < n; i++) {
      m.cp().post(sum(x[i], c));
    }

    // in each column exactly c coins must be placed
    for (int j = 0; j < n; j++) {
      CPIntVar[] column = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        column[i] = x[i][j];
      }
      m.cp().post(sum(column, c));
    }

    // every way to place c coins in a line of n cells, given as 0/1 patterns
    List<Integer> masks = new ArrayList<>();
    for (int mask = 0; mask < (1 << n); mask++) {
      if (Integer.bitCount(mask) == c) {
        masks.add(mask);
      }
    }

    // the cost of row i is the sum of the costs of its coins. A row table
    // lists the patterns of the row together with that cost, so the cost
    // follows the cells exactly and the search prunes on it.
    CPIntVar[] rowCost = new CPIntVar[n];
    int rowLo = 0;
    int rowHi = 0;
    for (int i = 0; i < n; i++) {
      int[][] rows = new int[masks.size()][n + 1];
      int lo = Integer.MAX_VALUE;
      int hi = Integer.MIN_VALUE;
      for (int r = 0; r < masks.size(); r++) {
        int mask = masks.get(r);
        int cost = 0;
        for (int j = 0; j < n; j++) {
          int bit = (mask >> j) & 1;
          rows[r][j] = bit;
          if (bit == 1) {
            cost += (i - j) * (i - j);
          }
        }
        rows[r][n] = cost;
        lo = Math.min(lo, cost);
        hi = Math.max(hi, cost);
      }
      rowLo += lo;
      rowHi += hi;
      rowCost[i] = makeIntVar(m.cp(), lo, hi);
      CPIntVar[] scope = new CPIntVar[n + 1];
      System.arraycopy(x[i], 0, scope, 0, n);
      scope[n] = rowCost[i];
      // the coins of row i form one of its patterns, with that row's cost
      m.cp().post(table(scope, rows));
    }

    // the cost of column j is the sum of the costs of its coins, the same
    // way as for the rows, with the column table
    CPIntVar[] colCost = new CPIntVar[n];
    int colLo = 0;
    int colHi = 0;
    for (int j = 0; j < n; j++) {
      int[][] cols = new int[masks.size()][n + 1];
      int lo = Integer.MAX_VALUE;
      int hi = Integer.MIN_VALUE;
      for (int r = 0; r < masks.size(); r++) {
        int mask = masks.get(r);
        int cost = 0;
        for (int i = 0; i < n; i++) {
          int bit = (mask >> i) & 1;
          cols[r][i] = bit;
          if (bit == 1) {
            cost += (i - j) * (i - j);
          }
        }
        cols[r][n] = cost;
        lo = Math.min(lo, cost);
        hi = Math.max(hi, cost);
      }
      colLo += lo;
      colHi += hi;
      colCost[j] = makeIntVar(m.cp(), lo, hi);
      CPIntVar[] scope = new CPIntVar[n + 1];
      for (int i = 0; i < n; i++) {
        scope[i] = x[i][j];
      }
      scope[n] = colCost[j];
      m.cp().post(table(scope, cols));
    }

    // the total cost is the sum over the rows, and also the sum over the columns
    int zLo = Math.max(rowLo, colLo);
    int zHi = Math.min(rowHi, colHi);
    CPIntVar z = makeIntVar(m.cp(), zLo, zHi);
    m.cp().post(sum(rowCost, z));
    m.cp().post(sum(colCost, z));

    // the sum of the quadratic horizontal distance from the main diagonal of
    // all cells containing a coin must be as small as possible
    m.minimize(z);

    out.put("x", x);
    out.put("z", z);
  }
}
