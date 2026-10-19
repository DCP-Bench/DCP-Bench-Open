import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Flip the sign of entire rows and columns so that every row and every column sums to a
// positive number or zero, and minimise the overall sum of the resulting array.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] a = inst.getIntMatrix("input_matrix");
    int R = a.length;
    int C = a[0].length;

    // one flip variable per row and per column; 1 means the sign is flipped
    CPBoolVar[] rowFlip = m.boolVarArray(R);
    CPBoolVar[] colFlip = m.boolVarArray(C);

    // the value of each cell after flipping: its sign is negative exactly when the row flip and the column flip differ
    CPIntVar[][] cell = new CPIntVar[R][C];
    int bound = 0;
    for (int i = 0; i < R; i++) {
      for (int j = 0; j < C; j++) {
        int v = a[i][j];
        int b = Math.abs(v);
        bound += b;
        CPIntVar e = m.intVar(-b, b);
        // the value of cell (i, j) is v when both flips agree, and -v when they differ
        m.cp().post(table(
            new CPIntVar[] {rowFlip[i], colFlip[j], e},
            new int[][] {{0, 0, v}, {0, 1, -v}, {1, 0, -v}, {1, 1, v}}));
        cell[i][j] = e;
      }
    }

    // every row sums to a positive number or zero
    for (int i = 0; i < R; i++) {
      m.cp().post(ge(sum(cell[i]), 0));
    }

    // every column sums to a positive number or zero
    for (int j = 0; j < C; j++) {
      CPIntVar[] col = new CPIntVar[R];
      for (int i = 0; i < R; i++) col[i] = cell[i][j];
      m.cp().post(ge(sum(col), 0));
    }

    // the overall sum of the array is the objective, held in a plain variable over its bounds
    CPIntVar[] all = new CPIntVar[R * C];
    for (int i = 0; i < R; i++)
      for (int j = 0; j < C; j++) all[i * C + j] = cell[i][j];
    // the total is a sum of non-negative row sums, so it is never negative
    CPIntVar obj = m.intVar(0, bound);
    m.cp().post(eq(obj, sum(all)));
    m.minimize(obj);

    // row and column signs: -1 when flipped, 1 otherwise
    CPIntVar[] rowSign = new CPIntVar[R];
    for (int i = 0; i < R; i++) rowSign[i] = plus(mul(rowFlip[i], -2), 1);
    CPIntVar[] colSign = new CPIntVar[C];
    for (int j = 0; j < C; j++) colSign[j] = plus(mul(colFlip[j], -2), 1);

    out.put("row_signs", rowSign);
    out.put("col_signs", colSign);
  }
}
