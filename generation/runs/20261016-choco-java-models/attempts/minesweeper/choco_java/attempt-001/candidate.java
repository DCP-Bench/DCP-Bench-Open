// Minesweeper: decide which unopened cells of the board hide a mine, from the numbers shown on the
// opened cells. A number on an opened cell is the count of mines among its adjacent cells (8 neighbours).
// Opened cells contain no mine.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] game = inst.getIntMatrix("game_data");
    int unopened = inst.getInt("X");          // value marking an unopened cell
    int rows = game.length;
    int cols = game[0].length;

    // mine[r][c] = 1 if the cell at row r, column c holds a mine
    BoolVar[][] mine = new BoolVar[rows][cols];
    for (int r = 0; r < rows; r++)
      for (int c = 0; c < cols; c++)
        mine[r][c] = m.boolVar("mine_" + r + "_" + c);

    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        if (game[r][c] == unopened) continue;   // unopened cell: no clue, nothing to check

        // an opened cell contains no mine
        mine[r][c].eq(0).post();

        // the number on an opened cell counts the mines among its adjacent cells
        java.util.List<BoolVar> around = new java.util.ArrayList<>();
        for (int dr = -1; dr <= 1; dr++)
          for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) continue;
            int nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) around.add(mine[nr][nc]);
          }
        m.sum(around.toArray(new BoolVar[0]), "=", game[r][c]).post();
      }
    }

    out.put("mines", mine);
  }
}
