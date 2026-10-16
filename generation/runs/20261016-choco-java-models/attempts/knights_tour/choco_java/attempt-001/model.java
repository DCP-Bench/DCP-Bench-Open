import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Knight's tour on an n x n board: a sequence of knight moves that visits every
// square exactly once, without returning to the starting square.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int nn = n * n;

    // x[i][j]: the move number at which the knight visits square (i, j)
    IntVar[][] x = m.intVarMatrix("x", n, n, 0, nn - 1);

    // flatten the board: square s = i * n + j
    IntVar[] flat = new IntVar[nn];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++) flat[i * n + j] = x[i][j];

    // every square is visited exactly once, at a distinct move number
    m.allDifferent(flat, "AC").post();

    // cellOf[p]: the square visited at move p (the inverse of x)
    IntVar[] cellOf = m.intVarArray("cellOf", nn, 0, nn - 1);
    m.inverseChanneling(flat, cellOf).post();

    // knight moves between two squares: differences (1,2) or (2,1) in either sign
    Tuples moves = new Tuples(true);
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++)
        for (int di = -2; di <= 2; di++)
          for (int dj = -2; dj <= 2; dj++) {
            if (Math.abs(di) * Math.abs(dj) != 2) continue;
            int ii = i + di, jj = j + dj;
            if (ii < 0 || ii >= n || jj < 0 || jj >= n) continue;
            moves.add(i * n + j, ii * n + jj);
          }

    // each move goes from the square of one move to a knight's move away
    // (the walk is open: the last square has no successor, and there is no return move)
    for (int p = 0; p + 1 < nn; p++) {
      m.table(new IntVar[]{cellOf[p], cellOf[p + 1]}, moves).post();
    }

    // branch on the squares in move order, smallest domain first
    Solver s = m.getSolver();
    s.setSearch(Search.minDomLBSearch(cellOf));

    out.put("x", x);
  }
}
