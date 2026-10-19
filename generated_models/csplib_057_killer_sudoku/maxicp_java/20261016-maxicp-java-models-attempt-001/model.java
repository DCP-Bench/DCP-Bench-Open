// Killer sudoku: fill a 9x9 grid with the numbers 1 to 9 so that the conditions below hold.
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int size = 9;
    int block = 3;

    // the grid is filled with numbers from 1 to 9
    CPIntVar[][] x = new CPIntVar[size][size];
    for (int r = 0; r < size; r++) {
      for (int c = 0; c < size; c++) {
        x[r][c] = m.intVar(1, size);
      }
    }

    // each row contains each number exactly once
    for (int r = 0; r < size; r++) {
      m.cp().post(allDifferent(x[r]));
    }

    // each column contains each number exactly once
    for (int c = 0; c < size; c++) {
      CPIntVar[] column = new CPIntVar[size];
      for (int r = 0; r < size; r++) {
        column[r] = x[r][c];
      }
      m.cp().post(allDifferent(column));
    }

    // each nonet contains each number exactly once
    for (int br = 0; br < block; br++) {
      for (int bc = 0; bc < block; bc++) {
        CPIntVar[] nonet = new CPIntVar[size];
        int k = 0;
        for (int dr = 0; dr < block; dr++) {
          for (int dc = 0; dc < block; dc++) {
            nonet[k++] = x[block * br + dr][block * bc + dc];
          }
        }
        m.cp().post(allDifferent(nonet));
      }
    }

    // each cage: the cage cells are read from the instance, as 1-based row and column pairs
    JsonArray cages = inst.raw("problem").getAsJsonArray();
    for (JsonElement element : cages) {
      JsonArray cage = element.getAsJsonArray();
      int total = cage.get(0).getAsInt();
      JsonArray cells = cage.get(1).getAsJsonArray();
      CPIntVar[] cellVars = new CPIntVar[cells.size()];
      for (int i = 0; i < cells.size(); i++) {
        JsonArray rc = cells.get(i).getAsJsonArray();
        cellVars[i] = x[rc.get(0).getAsInt() - 1][rc.get(1).getAsInt() - 1];
      }

      // the sum of all numbers in a cage matches the small number printed in its corner
      m.cp().post(eq(sum(cellVars), total));

      // no number appears more than once in a cage
      m.cp().post(allDifferent(cellVars));
    }

    out.put("x", x);
  }
}
