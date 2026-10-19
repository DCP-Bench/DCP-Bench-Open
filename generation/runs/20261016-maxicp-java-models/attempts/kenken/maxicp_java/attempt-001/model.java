import static org.maxicp.cp.CPFactory.*;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPIntVar;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// KenKen: fill an n x n grid with the digits 1..n so that every row and every column
// holds each digit exactly once, and every cage (a group of cells with a target value)
// achieves its target with some arithmetic operation on its digits.
public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the grid of digits, each cell a digit from 1 to n
    CPIntVar[][] x = new CPIntVar[n][n];
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) {
        x[r][c] = m.intVar(1, n);
      }
    }

    // each row contains exactly one of each digit
    for (int r = 0; r < n; r++) {
      m.cp().post(allDifferent(x[r]));
    }

    // each column contains exactly one of each digit
    for (int c = 0; c < n; c++) {
      CPIntVar[] column = new CPIntVar[n];
      for (int r = 0; r < n; r++) column[r] = x[r][c];
      m.cp().post(allDifferent(column));
    }

    // each bold-outlined cage: its digits achieve the cage's target
    // (the operation is not given in the instance, so any operation that fits the cage is allowed)
    JsonArray cages = inst.raw("problem").getAsJsonArray();
    for (JsonElement element : cages) {
      JsonArray cage = element.getAsJsonArray();
      int target = cage.get(0).getAsInt();
      JsonArray cells = cage.get(1).getAsJsonArray();

      int k = cells.size();
      CPIntVar[] cageVars = new CPIntVar[k];
      for (int i = 0; i < k; i++) {
        JsonArray cell = cells.get(i).getAsJsonArray();
        int row = cell.get(0).getAsInt() - 1; // cells are 1-based in the instance
        int col = cell.get(1).getAsInt() - 1;
        cageVars[i] = x[row][col];
      }

      // the digits of the cage, as every tuple of digits that achieves the target
      List<int[]> allowed = new ArrayList<>();
      int[] digits = new int[k];
      enumerate(digits, 0, n, target, allowed);
      m.cp().post(table(cageVars, allowed.toArray(new int[0][])));
    }

    // the declared output: the solved grid
    out.put("x", x);
  }

  // every tuple of digits 1..n for the cage's cells that achieves the target
  private static void enumerate(int[] digits, int pos, int n, int target, List<int[]> allowed) {
    if (pos == digits.length) {
      if (achieves(digits, target)) allowed.add(digits.clone());
      return;
    }
    for (int v = 1; v <= n; v++) {
      digits[pos] = v;
      enumerate(digits, pos + 1, n, target, allowed);
    }
  }

  // a single cell holds the target; a larger cage has digits that sum or multiply to the target;
  // a two-cell cage may also have digits that differ by the target or divide to it
  private static boolean achieves(int[] digits, int target) {
    int k = digits.length;
    if (k == 1) return digits[0] == target;
    long sum = 0;
    long product = 1;
    for (int d : digits) {
      sum += d;
      product *= d;
    }
    if (sum == target || product == target) return true;
    if (k == 2) {
      int lo = Math.min(digits[0], digits[1]);
      int hi = Math.max(digits[0], digits[1]);
      if (hi - lo == target) return true;
      if (hi % lo == 0 && hi / lo == target) return true;
    }
    return false;
  }
}
