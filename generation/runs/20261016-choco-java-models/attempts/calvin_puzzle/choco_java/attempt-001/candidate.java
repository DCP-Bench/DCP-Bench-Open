import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Calvin puzzle: fill an n by n grid with the numbers 1..n*n, each once, so that every
// number follows the previous one either three squares away horizontally or vertically,
// or two squares away diagonally.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cells = n * n;

    // seq[k]: cell (row * n + col) holding the number k + 1
    IntVar[] seq = m.intVarArray("seq", cells, 0, cells - 1);
    m.allDifferent(seq, "AC").post();

    // cellOf[c]: index k of the number in cell c, so that the grid is the inverse of seq
    IntVar[] cellOf = m.intVarArray("cellOf", cells, 0, cells - 1);
    m.inverseChanneling(seq, cellOf).post();
    IntVar[][] x = m.intVarMatrix("x", n, n, 1, cells);
    for (int c = 0; c < cells; c++)
      m.arithm(x[c / n][c % n], "-", cellOf[c], "=", 1).post();

    // legal moves between a cell a and the next cell b:
    // Type I: same row or column, three squares apart; Type II: diagonal, two squares apart
    Tuples moves = new Tuples(true);
    for (int a = 0; a < cells; a++) {
      int ra = a / n, ca = a % n;
      for (int b = 0; b < cells; b++) {
        int rb = b / n, cb = b % n;
        int dr = Math.abs(ra - rb), dc = Math.abs(ca - cb);
        boolean typeI = (dr == 3 && dc == 0) || (dr == 0 && dc == 3);
        boolean typeII = dr == 2 && dc == 2;
        if (typeI || typeII) moves.add(a, b);
      }
    }

    // each number follows the previous one by a legal move
    for (int k = 0; k < cells - 1; k++)
      m.table(new IntVar[]{seq[k], seq[k + 1]}, moves).post();

    m.getSolver().setSearch(Search.inputOrderLBSearch(seq));

    out.put("x", x);
  }
}
