import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import dcp.Instance;
import dcp.Outputs;

// Kakuro: fill each white cell with a digit from 1 to 9 so that the digits of every entry
// (a run of white cells across or down) sum to the clue printed for it, and no digit is
// repeated within an entry. Black and clue cells are output as 0.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");                      // grid side
    int[][] blanks = inst.getIntMatrix("blanks");  // non-white cells, 1-based [row, col]
    JsonArray entries = inst.raw("problem").getAsJsonArray();  // [clue, [row, col], ...], 1-based

    // the white cells: every cell an entry covers
    boolean[][] white = new boolean[n][n];
    for (JsonElement el : entries) {
      JsonArray entry = el.getAsJsonArray();
      for (int i = 1; i < entry.size(); i++) {
        JsonArray rc = entry.get(i).getAsJsonArray();
        white[rc.get(0).getAsInt() - 1][rc.get(1).getAsInt() - 1] = true;
      }
    }

    // a white cell holds a digit from 1 to 9; every other cell is 0
    IntVar[][] x = new IntVar[n][n];
    for (int r = 0; r < n; r++)
      for (int c = 0; c < n; c++)
        x[r][c] = white[r][c] ? m.intVar("x" + (r + 1) + "_" + (c + 1), 1, 9) : m.intVar(0);

    // blanks lists the non-white cells; they must be the cells left out above
    int whiteCount = 0;
    for (boolean[] row : white) for (boolean w : row) if (w) whiteCount++;
    if (whiteCount + blanks.length != n * n) throw new IllegalStateException("blanks and entries do not partition the grid");

    IntVar[] whiteVars = new IntVar[whiteCount];
    int k = 0;
    for (int r = 0; r < n; r++)
      for (int c = 0; c < n; c++) if (white[r][c]) whiteVars[k++] = x[r][c];

    for (JsonElement el : entries) {
      JsonArray entry = el.getAsJsonArray();
      int clue = entry.get(0).getAsInt();
      IntVar[] cells = new IntVar[entry.size() - 1];
      for (int i = 1; i < entry.size(); i++) {
        JsonArray rc = entry.get(i).getAsJsonArray();
        cells[i - 1] = x[rc.get(0).getAsInt() - 1][rc.get(1).getAsInt() - 1];
      }

      // the digits of the entry sum to its clue
      m.sum(cells, "=", clue).post();

      // no digit is repeated within the entry
      m.allDifferent(cells, "AC").post();
    }

    m.getSolver().setSearch(Search.minDomLBSearch(whiteVars));

    out.put("x", x);
  }
}
