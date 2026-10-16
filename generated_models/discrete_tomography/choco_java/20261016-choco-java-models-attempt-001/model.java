// Discrete tomography: reconstruct a 0/1 matrix from the number of ones in each row and
// in each column (the row sums and column sums are given by the instance).
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] rowSums = inst.getIntArray("row_sums");
    int[] colSums = inst.getIntArray("col_sums");
    int rows = rowSums.length;
    int cols = colSums.length;

    // x[r][c] = 1 if the matrix cell in row r and column c holds a one
    BoolVar[][] x = m.boolVarMatrix("x", rows, cols);

    // each row contains as many ones as its row sum (the horizontal x-ray)
    for (int r = 0; r < rows; r++) {
      m.sum(x[r], "=", rowSums[r]).post();
    }

    // each column contains as many ones as its column sum (the vertical x-ray)
    for (int c = 0; c < cols; c++) {
      BoolVar[] column = new BoolVar[rows];
      for (int r = 0; r < rows; r++) column[r] = x[r][c];
      m.sum(column, "=", colSums[c]).post();
    }

    out.put("matrix", x);
  }
}
