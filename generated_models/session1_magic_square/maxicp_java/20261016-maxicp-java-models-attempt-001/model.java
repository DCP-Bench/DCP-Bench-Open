import org.maxicp.cp.engine.core.CPIntVar;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import static org.maxicp.cp.CPFactory.*;

// Magic square of order n: an n x n grid holding each integer from 1 to n*n exactly once,
// with every row, column and both diagonals summing to n(n^2+1)/2.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cells = n * n;
    // the magic sum is n(n^2+1)/2, an integer for every allowed n
    int magic = n * (cells + 1) / 2;

    // the grid holds the numbers 1 to n^2, one per cell
    CPIntVar[] sq = m.intVarArray(cells, 1, cells);
    CPIntVar[][] grid = new CPIntVar[n][n];
    for (int r = 0; r < n; r++)
      for (int c = 0; c < n; c++) grid[r][c] = sq[r * n + c];

    // each cell contains a different integer
    m.cp().post(allDifferent(sq));

    // the sum of the integers in each row is the magic sum
    for (int r = 0; r < n; r++) m.cp().post(sum(grid[r], magic));

    // the sum of the integers in each column is the magic sum
    for (int c = 0; c < n; c++) {
      CPIntVar[] column = new CPIntVar[n];
      for (int r = 0; r < n; r++) column[r] = grid[r][c];
      m.cp().post(sum(column, magic));
    }

    // the sum of the integers on the main diagonal is the magic sum
    CPIntVar[] mainDiag = new CPIntVar[n];
    for (int i = 0; i < n; i++) mainDiag[i] = grid[i][i];
    m.cp().post(sum(mainDiag, magic));

    // the sum of the integers on the anti-diagonal is the magic sum
    CPIntVar[] antiDiag = new CPIntVar[n];
    for (int i = 0; i < n; i++) antiDiag[i] = grid[i][n - 1 - i];
    m.cp().post(sum(antiDiag, magic));

    out.put("square", grid);
  }
}
