import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Magic square: place the integers 1..n^2, each once, in an n x n grid so that
// every row, column and both diagonals sum to the same value n(n^2+1)/2.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int nn = n * n;
    // the common sum of each row, column and diagonal, from the size n
    int magic = n * (nn + 1) / 2;

    // square[r][c]: the integer in row r, column c
    IntVar[][] square = m.intVarMatrix("square", n, n, 1, nn);

    // flat view of all cells, for the distinctness constraint
    IntVar[] cells = new IntVar[nn];
    for (int r = 0; r < n; r++)
      for (int c = 0; c < n; c++)
        cells[r * n + c] = square[r][c];

    // each cell contains a different integer from 1 to n^2
    m.allDifferent(cells, "AC").post();

    // the sum of the integers in each row is the magic sum
    for (int r = 0; r < n; r++)
      m.sum(square[r], "=", magic).post();

    // the sum of the integers in each column is the magic sum
    for (int c = 0; c < n; c++) {
      IntVar[] column = new IntVar[n];
      for (int r = 0; r < n; r++) column[r] = square[r][c];
      m.sum(column, "=", magic).post();
    }

    // the sum on the main diagonal is the magic sum
    IntVar[] diagonal = new IntVar[n];
    // the sum on the anti-diagonal is the magic sum
    IntVar[] antiDiagonal = new IntVar[n];
    for (int i = 0; i < n; i++) {
      diagonal[i] = square[i][i];
      antiDiagonal[i] = square[i][n - 1 - i];
    }
    m.sum(diagonal, "=", magic).post();
    m.sum(antiDiagonal, "=", magic).post();

    // branch on the cells with dom/wdeg, and restart with Luby to escape bad early choices
    m.getSolver().setSearch(Search.domOverWDegSearch(cells));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("square", square);
  }
}
