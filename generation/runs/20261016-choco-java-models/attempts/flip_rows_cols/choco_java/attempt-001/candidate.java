import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Flip rows and columns of a matrix of signed numbers so that every row and every column
// sums to a non-negative number, and the overall sum is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] a = inst.getIntMatrix("input_matrix");
    int rows = a.length;
    int cols = a[0].length;

    // row_signs[i] = -1 or 1: whether row i is flipped
    IntVar[] rowSigns = new IntVar[rows];
    for (int i = 0; i < rows; i++) rowSigns[i] = m.intVar("row_sign_" + i, new int[]{-1, 1});

    // col_signs[j] = -1 or 1: whether column j is flipped
    IntVar[] colSigns = new IntVar[cols];
    for (int j = 0; j < cols; j++) colSigns[j] = m.intVar("col_sign_" + j, new int[]{-1, 1});

    // flipped cell: the cell is negated when exactly one of its row and column is flipped
    IntVar[][] flipped = new IntVar[rows][cols];
    for (int i = 0; i < rows; i++) {
      for (int j = 0; j < cols; j++) {
        int bound = Math.abs(a[i][j]);
        IntVar sign = m.intVar(-1, 1);
        m.times(rowSigns[i], colSigns[j], sign).post();
        flipped[i][j] = m.intVar("cell_" + i + "_" + j, -bound, bound);
        m.scalar(new IntVar[]{sign}, new int[]{a[i][j]}, "=", flipped[i][j]).post();
      }
    }

    // every row sums to a positive number or zero
    for (int i = 0; i < rows; i++) {
      m.sum(flipped[i], ">=", 0).post();
    }

    // every column sums to a positive number or zero
    for (int j = 0; j < cols; j++) {
      IntVar[] column = new IntVar[rows];
      for (int i = 0; i < rows; i++) column[i] = flipped[i][j];
      m.sum(column, ">=", 0).post();
    }

    // the overall sum of the flipped matrix, minimised
    IntVar[] all = new IntVar[rows * cols];
    for (int i = 0; i < rows; i++)
      for (int j = 0; j < cols; j++) all[i * cols + j] = flipped[i][j];
    IntVar total = m.sum("total", all);
    m.setObjective(Model.MINIMIZE, total);

    out.put("row_signs", rowSigns);
    out.put("col_signs", colSigns);
  }
}
