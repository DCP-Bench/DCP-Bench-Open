import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Quasigroup completion: complete a partially filled order m quasigroup.
// The instance gives the order N and the partially filled square start (0 marks an empty cell).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("N");
    int[][] start = inst.getIntMatrix("start");

    // an order m quasigroup is a Latin square of size m: each element from 1 to m
    // occurs in the m x m table
    CPIntVar[][] puzzle = new CPIntVar[n][];
    for (int i = 0; i < n; i++) {
      puzzle[i] = m.intVarArray(n, 1, n);
    }

    // every row holds each element exactly once
    for (int i = 0; i < n; i++) {
      m.cp().post(allDifferent(puzzle[i]));
    }

    // every column holds each element exactly once
    for (int j = 0; j < n; j++) {
      CPIntVar[] column = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        column[i] = puzzle[i][j];
      }
      m.cp().post(allDifferent(column));
    }

    // the given elements of the partially filled quasigroup keep their values
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if (start[i][j] != 0) {
          m.cp().post(eq(puzzle[i][j], start[i][j]));
        }
      }
    }

    // print the completed quasigroup
    out.put("puzzle", puzzle);
  }
}
