import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// KenKen: fill an n x n grid with the digits 1..n so that each row and each column holds
// every digit once, and each cage (a group of cells with a target) reaches its target by
// one of the operations +, -, x or /. The instance does not name the operation of a cage.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    // problem: a list of [target, [[row, col], ...]] with 1-based cells
    JsonArray cages = inst.raw("problem").getAsJsonArray();

    IntVar[][] x = m.intVarMatrix("x", n, n, 1, n);

    // each row contains exactly one of each digit
    for (int r = 0; r < n; r++) m.allDifferent(x[r], "AC").post();

    // each column contains exactly one of each digit
    for (int c = 0; c < n; c++) {
      IntVar[] column = new IntVar[n];
      for (int r = 0; r < n; r++) column[r] = x[r][c];
      m.allDifferent(column, "AC").post();
    }

    // each cage achieves its result with one of the operations
    for (JsonElement element : cages) {
      JsonArray cage = element.getAsJsonArray();
      int target = cage.get(0).getAsInt();
      JsonArray cellsJson = cage.get(1).getAsJsonArray();
      IntVar[] cells = new IntVar[cellsJson.size()];
      for (int i = 0; i < cells.length; i++) {
        JsonArray rc = cellsJson.get(i).getAsJsonArray();
        cells[i] = x[rc.get(0).getAsInt() - 1][rc.get(1).getAsInt() - 1];
      }

      // a single cell holds the target itself
      if (cells.length == 1) {
        m.arithm(cells[0], "=", target).post();
        continue;
      }

      // the operation of the cage is not given, so list the operations that fit its size
      List<BoolVar> options = new ArrayList<>();

      // addition: the cells sum to the target
      BoolVar isSum = m.boolVar();
      m.sum(cells, "=", target).reifyWith(isSum);
      options.add(isSum);

      // multiplication: the cells multiply to the target
      IntVar product = cells[0];
      for (int i = 1; i < cells.length; i++) product = product.mul(cells[i]).intVar();
      options.add(product.eq(target).boolVar());

      // subtraction and division are for two cells: the larger minus the smaller, or the
      // larger divided by the smaller, is the target
      if (cells.length == 2) {
        BoolVar isDiff = m.boolVar();
        m.arithm(cells[0], "-", cells[1], "=", target).reifyWith(isDiff);
        options.add(isDiff);
        BoolVar isDiffRev = m.boolVar();
        m.arithm(cells[1], "-", cells[0], "=", target).reifyWith(isDiffRev);
        options.add(isDiffRev);

        // exact quotient: first = target * second, or second = target * first
        BoolVar isQuot = m.boolVar();
        m.scalar(new IntVar[]{cells[0], cells[1]}, new int[]{1, -target}, "=", 0).reifyWith(isQuot);
        options.add(isQuot);
        BoolVar isQuotRev = m.boolVar();
        m.scalar(new IntVar[]{cells[1], cells[0]}, new int[]{1, -target}, "=", 0).reifyWith(isQuotRev);
        options.add(isQuotRev);
      }

      // the cage's operation is one of the options
      m.sum(options.toArray(new BoolVar[0]), ">=", 1).post();
    }

    out.put("x", x);
  }
}
