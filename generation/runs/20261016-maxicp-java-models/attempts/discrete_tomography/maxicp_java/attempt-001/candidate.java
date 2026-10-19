import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Discrete tomography: a matrix of zeroes and ones is x-rayed by the number of
// ones in each row and in each column. Reconstruct a matrix that has these sums.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the row sums and column sums of the x-ray; their lengths give the matrix size
    int[] rowSums = inst.getIntArray("row_sums");
    int[] colSums = inst.getIntArray("col_sums");
    int rows = rowSums.length;
    int cols = colSums.length;

    // matrix[i][j] = 1 if the cell in row i and column j contains a one, 0 otherwise
    CPBoolVar[][] matrix = new CPBoolVar[rows][cols];
    for (int i = 0; i < rows; i++) {
      for (int j = 0; j < cols; j++) {
        matrix[i][j] = m.boolVar();
      }
    }

    // the number of ones in each row is the row sum
    for (int i = 0; i < rows; i++) {
      m.cp().post(eq(sum(matrix[i]), rowSums[i]));
    }

    // the number of ones in each column is the column sum
    for (int j = 0; j < cols; j++) {
      CPIntVar[] column = new CPIntVar[rows];
      for (int i = 0; i < rows; i++) {
        column[i] = matrix[i][j];
      }
      m.cp().post(eq(sum(column), colSums[j]));
    }

    out.put("matrix", matrix);
  }
}
