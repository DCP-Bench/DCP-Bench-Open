import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Kakuro: insert a digit from 1 to 9 into each white cell of an n x n grid so that
// the digits of each entry add up to its clue, and no digit is repeated in an entry.
// Output x is the grid, with 0 for a blank (non-white) cell.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the blanks are the cells that are not white (clue and black cells), 1-based
    boolean[][] blank = new boolean[n][n];
    int[][] blanks = inst.getIntMatrix("blanks");
    for (int[] b : blanks) {
      blank[b[0] - 1][b[1] - 1] = true;
    }

    // one grid cell per position: a digit 1..9 on a white cell, 0 on a blank one
    CPIntVar[][] x = new CPIntVar[n][n];
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) {
        x[r][c] = blank[r][c] ? m.intVar(0, 0) : m.intVar(1, 9);
      }
    }

    // each entry is a clue followed by the positions of its cells, 1-based
    JsonArray entries = inst.raw("problem").getAsJsonArray();
    for (JsonElement el : entries) {
      JsonArray entry = el.getAsJsonArray();
      int clue = entry.get(0).getAsInt();
      CPIntVar[] cells = new CPIntVar[entry.size() - 1];
      for (int k = 1; k < entry.size(); k++) {
        JsonArray p = entry.get(k).getAsJsonArray();
        cells[k - 1] = x[p.get(0).getAsInt() - 1][p.get(1).getAsInt() - 1];
      }

      // no digit is duplicated in any entry
      m.cp().post(allDifferent(cells));

      // the digits of each entry add up to its clue
      m.cp().post(sum(cells, clue));
    }

    out.put("x", x);
  }
}
