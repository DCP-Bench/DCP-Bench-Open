import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.nary.automata.FA.FiniteAutomaton;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Nonogram: shade cells of a rows x cols grid (1 shaded, 0 empty) so that the shaded
// blocks in every row and every column are the consecutive runs given by its clue.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int rows = inst.getInt("rows"), cols = inst.getInt("cols");
    int[][] rowRules = inst.getIntMatrix("row_rules");  // per row: block lengths, zero padded at the front
    int[][] colRules = inst.getIntMatrix("col_rules");  // per column: block lengths, zero padded at the front
    IntVar[][] board = m.intVarMatrix("board", rows, cols, 0, 1);

    // each row's shaded blocks, read left to right, are its clue
    for (int r = 0; r < rows; r++) {
      m.regular(board[r], new FiniteAutomaton(clueExpression(rowRules[r]))).post();
    }

    // each column's shaded blocks, read top to bottom, are its clue
    for (int c = 0; c < cols; c++) {
      IntVar[] column = new IntVar[rows];
      for (int r = 0; r < rows; r++) column[r] = board[r][c];
      m.regular(column, new FiniteAutomaton(clueExpression(colRules[c]))).post();
    }

    out.put("board", board);
  }

  // Regular expression for one clue: any run of empty cells, then the blocks in order,
  // with at least one empty cell between two blocks. Zeros in the clue are padding.
  static String clueExpression(int[] clue) {
    StringBuilder sb = new StringBuilder("0*");
    boolean first = true;
    for (int block : clue) {
      if (block == 0) continue;
      if (!first) sb.append("0+");
      sb.append("1{").append(block).append(",").append(block).append("}");
      first = false;
    }
    sb.append("0*");
    return sb.toString();
  }
}
