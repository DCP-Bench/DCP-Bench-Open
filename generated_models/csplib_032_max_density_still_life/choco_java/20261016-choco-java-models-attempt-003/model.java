import org.chocosolver.solver.Model;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

// Max-density still life: choose live/dead cells on an n x m grid (cells outside the grid
// are dead) so that the pattern is stable under Conway's Game of Life, maximising live cells.
public class Submission {
  // lazy clause generation: the constraints used here (arithmetic, sums, reified implications,
  // lexicographic order) are on its checked list, and it learns from the failures of the proof
  public static SettingsBuilder settings() {
    return SettingsBuilder.init().setLCG(true);
  }

  public static void build(Instance inst, Model m, Outputs out) {
    int rows = inst.getInt("n");
    int cols = inst.getInt("m");

    // grid[i][j] = 1 if cell (i,j) of the active grid is live
    BoolVar[][] grid = m.boolVarMatrix("grid", rows, cols);

    // a live cell has 2 or 3 live neighbours; a dead cell does not have exactly 3
    for (int r = -1; r <= rows; r++) {
      for (int c = -1; c <= cols; c++) {
        // live in-grid neighbours of cell (r,c)
        List<IntVar> nbrs = new ArrayList<>();
        for (int dr = -1; dr <= 1; dr++) {
          for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) continue;
            int rr = r + dr, cc = c + dc;
            if (rr >= 0 && rr < rows && cc >= 0 && cc < cols) nbrs.add(grid[rr][cc]);
          }
        }
        IntVar[] nb = nbrs.toArray(new IntVar[0]);

        if (r >= 0 && r < rows && c >= 0 && c < cols) {
          BoolVar live = grid[r][c];
          IntVar count = m.intVar("neighbours_" + r + "_" + c, 0, 8);
          m.sum(nb, "=", count).post();

          // a live cell has exactly 2 or 3 live neighbours
          m.ifThen(live, m.arithm(count, ">=", 2));
          m.ifThen(live, m.arithm(count, "<=", 3));

          // a dead cell does not have exactly 3 live neighbours
          m.ifThen(m.arithm(count, "=", 3), m.arithm(live, "=", 1));
        } else if (nb.length >= 3) {
          // a dead cell just outside the grid does not have exactly 3 live neighbours
          m.sum(nb, "!=", 3).post();
        }
      }
    }

    // symmetry breaking: the grid is lexicographically no larger than its image under each
    // symmetry of the rectangle (flips and half turn; the diagonal reflections and quarter turns
    // only when the grid is square). Every orbit keeps at least one such grid, so the optimum is kept.
    IntVar[] flat = new IntVar[rows * cols];
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) flat[i * cols + j] = grid[i][j];
    for (int code = 1; code <= 7; code++) {
      if (code >= 4 && rows != cols) break;
      IntVar[] image = new IntVar[rows * cols];
      for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
          int ti, tj;
          switch (code) {
            case 1: ti = rows - 1 - i; tj = j; break;            // vertical flip
            case 2: ti = i; tj = cols - 1 - j; break;            // horizontal flip
            case 3: ti = rows - 1 - i; tj = cols - 1 - j; break; // half turn
            case 4: ti = j; tj = i; break;                       // transpose
            case 5: ti = cols - 1 - j; tj = rows - 1 - i; break; // anti-transpose
            case 6: ti = j; tj = rows - 1 - i; break;            // quarter turn
            default: ti = cols - 1 - j; tj = i; break;           // quarter turn back
          }
          image[i * cols + j] = grid[ti][tj];
        }
      }
      m.lexLessEq(flat, image).post();
    }

    // maximise the number of live cells
    IntVar live = m.sum("live_cells", flat);
    m.setObjective(Model.MAXIMIZE, live);

    // branch on the cells with the activity-based heuristic (learns which cells cause failures)
    m.getSolver().setSearch(Search.activityBasedSearch(flat));

    out.put("grid", grid);
  }
}
