import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Minesweeper: a grid of cells, some of them mines. Revealed cells show a number (0 to 8)
// that is the count of mines among their neighbouring cells. Cells marked -1 are unrevealed.
// Determine which cells hold a mine.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the revealed board, -1 for an unrevealed cell, otherwise the number shown
    int[][] board = inst.getIntMatrix("game_data");
    int rows = board.length;
    int cols = board[0].length;

    // mines[r][c] is true when the cell in row r, column c contains a mine
    CPBoolVar[][] mines = new CPBoolVar[rows][];
    for (int r = 0; r < rows; r++) {
      mines[r] = m.boolVarArray(cols);
    }

    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        if (board[r][c] < 0) {
          continue; // unrevealed cell: no number to check against
        }
        // a revealed cell is open, so it cannot be a mine
        m.cp().post(eq(mines[r][c], 0));

        // the number on a revealed cell is the count of mines in its neighbouring cells
        List<CPBoolVar> neighbours = new ArrayList<>();
        for (int dr = -1; dr <= 1; dr++) {
          for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) {
              continue;
            }
            int nr = r + dr;
            int nc = c + dc;
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
              neighbours.add(mines[nr][nc]);
            }
          }
        }
        m.cp().post(eq(sum(neighbours.toArray(new CPBoolVar[0])), board[r][c]));
      }
    }

    // mines: which cells contain a mine, True for a mine
    out.put("mines", mines);
  }
}
