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

    // the still-life rules on the (centre, live neighbour count) pairs: a live cell has
    // 2 or 3 live neighbours; a dead cell does not have exactly 3 live neighbours.
    List<int[]> allowed = new ArrayList<>();
    for (int centre = 0; centre <= 1; centre++)
      for (int count = 0; count <= 8; count++) {
        boolean ok = centre == 1 ? (count == 2 || count == 3) : count != 3;
        if (ok) allowed.add(new int[] {centre, count});
      }
    int[][] rows = allowed.toArray(new int[0][]);

    // every cell of the board, including the dead ring just outside the grid (rows 0 and
    // n+1, columns 0 and cols+1 of the padded board), gets a neighbour count that is the
    // sum of its live neighbours inside the grid; the rule is a table on (centre, count)
    for (int r = 0; r < n + 2; r++) {
      for (int c = 0; c < cols + 2; c++) {
        List<CPIntVar> neighbours = new ArrayList<>();
        for (int dr = -1; dr <= 1; dr++)
          for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) continue;
            int i = r + dr - 1;
            int j = c + dc - 1;
            if (i >= 0 && i < n && j >= 0 && j < cols) neighbours.add(grid[i][j]);
          }
        // the number of live neighbours of this cell
        CPIntVar count = makeIntVar(cp, 0, 8);
        cp.post(sum(neighbours.toArray(new CPIntVar[0]), count));

        // the centre of this board position: a grid cell, or the dead ring
        int ci = r - 1;
        int cj = c - 1;
        CPIntVar centre = (ci >= 0 && ci < n && cj >= 0 && cj < cols) ? grid[ci][cj] : dead;
        cp.post(table(new CPIntVar[] {centre, count}, rows));
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
}
