import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import dcp.Instance;
import dcp.Outputs;

// Killer sudoku: fill the n x n grid with digits 1..n so that each row, column and
// nonet holds every digit once, each cage's cells sum to the cage's printed total,
// and no digit repeats inside a cage.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");                       // grid side, 9
    int box = (int) Math.round(Math.sqrt(n));       // nonet side, 3
    IntVar[][] x = m.intVarMatrix("x", n, n, 1, n);

    // each row contains every digit exactly once
    for (int r = 0; r < n; r++) m.allDifferent(x[r], "AC").post();

    // each column contains every digit exactly once
    for (int c = 0; c < n; c++) {
      IntVar[] col = new IntVar[n];
      for (int r = 0; r < n; r++) col[r] = x[r][c];
      m.allDifferent(col, "AC").post();
    }

    // each nonet (3x3 box) contains every digit exactly once
    for (int br = 0; br < n; br += box) {
      for (int bc = 0; bc < n; bc += box) {
        IntVar[] nonet = new IntVar[n];
        for (int k = 0; k < n; k++) nonet[k] = x[br + k / box][bc + k % box];
        m.allDifferent(nonet, "AC").post();
      }
    }

    // each cage: cells listed as [row, col] with 1-based indices, followed by the printed sum
    JsonArray cages = inst.raw("problem").getAsJsonArray();
    for (JsonElement el : cages) {
      JsonArray cage = el.getAsJsonArray();
      int total = cage.get(0).getAsInt();
      JsonArray cells = cage.get(1).getAsJsonArray();
      IntVar[] cellVars = new IntVar[cells.size()];
      for (int i = 0; i < cells.size(); i++) {
        JsonArray rc = cells.get(i).getAsJsonArray();
        cellVars[i] = x[rc.get(0).getAsInt() - 1][rc.get(1).getAsInt() - 1];
      }

      // the sum of all numbers in a cage matches the small number printed in its corner
      m.sum(cellVars, "=", total).post();

      // no number appears more than once in a cage
      m.allDifferent(cellVars, "AC").post();
    }

    // branch on the grid cells, smallest domain first
    IntVar[] flat = new IntVar[n * n];
    for (int r = 0; r < n; r++)
      for (int c = 0; c < n; c++) flat[r * n + c] = x[r][c];
    m.getSolver().setSearch(Search.minDomLBSearch(flat));

    out.put("x", x);
  }
}
