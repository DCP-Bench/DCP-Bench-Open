import java.util.ArrayList;
import java.util.List;

import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Maximum density still life: on an n x m grid, choose which cells are alive so that the
// pattern is a still life (it does not change from one generation to the next) and the
// number of live cells is as large as possible. Cells outside the grid are dead and are
// part of the board, so the dead cells around the grid must obey the same rules.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cols = inst.getInt("m");
    var cp = m.cp();

    // decision variables: grid[i][j] = 1 if the cell in row i, column j is alive
    CPBoolVar[][] grid = new CPBoolVar[n][cols];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < cols; j++)
        grid[i][j] = m.boolVar();

    // constant dead cell, used for every cell outside the active grid
    CPIntVar dead = makeIntVar(cp, 0, 0);

    // the still-life rules for one cell and its eight neighbours, as a table over the nine
    // 0/1 values (centre first, then the neighbours). A live cell has 2 or 3 live neighbours;
    // a dead cell does not have exactly 3 live neighbours.
    List<int[]> allowed = new ArrayList<>();
    for (int code = 0; code < 512; code++) {
      int centre = code & 1;
      int live = 0;
      for (int b = 1; b < 9; b++) live += (code >> b) & 1;
      boolean ok = centre == 1 ? (live == 2 || live == 3) : live != 3;
      if (!ok) continue;
      int[] row = new int[9];
      for (int b = 0; b < 9; b++) row[b] = (code >> b) & 1;
      allowed.add(row);
    }
    int[][] rows = allowed.toArray(new int[0][]);

    // every cell of the board, including the dead ring just outside the grid (rows 0 and
    // n+1, columns 0 and cols+1 of the padded board), is the centre of one table
    for (int r = 0; r < n + 2; r++) {
      for (int c = 0; c < cols + 2; c++) {
        CPIntVar[] window = new CPIntVar[9];
        int k = 0;
        for (int dr = -1; dr <= 1; dr++)
          for (int dc = -1; dc <= 1; dc++) {
            window[k++] = cell(grid, dead, r + dr, c + dc, n, cols);
          }
        // the centre of the window must come first in the table
        CPIntVar[] ordered = new CPIntVar[9];
        ordered[0] = window[4];
        int j = 1;
        for (int q = 0; q < 9; q++) if (q != 4) ordered[j++] = window[q];
        cp.post(table(ordered, rows));
      }
    }

    // objective: maximise the number of live cells in the active grid
    CPIntVar[] flat = new CPIntVar[n * cols];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < cols; j++)
        flat[i * cols + j] = grid[i][j];
    m.maximize(sum(flat));

    out.put("grid", grid);
  }

  // the cell at padded position (row, col): row 0 and col 0 are the dead ring above and to
  // the left of the grid, so the active cell (i, j) sits at padded position (i+1, j+1)
  private static CPIntVar cell(CPBoolVar[][] grid, CPIntVar dead, int row, int col, int n, int cols) {
    int i = row - 1;
    int j = col - 1;
    if (i < 0 || i >= n || j < 0 || j >= cols) return dead;
    return grid[i][j];
  }
}
