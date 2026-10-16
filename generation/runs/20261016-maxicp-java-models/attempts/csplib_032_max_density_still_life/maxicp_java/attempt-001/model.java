import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Maximum density still life: on an n x m grid, choose which cells are alive so that the
// pattern is a still life (it does not change from one generation to the next) and the
// number of live cells is as large as possible. Cells outside the grid are dead and are
// part of the board, so the dead ring around the grid must obey the same rules.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cols = inst.getInt("m");
    var cp = m.cp();

    // constants used by the reified comparisons
    CPIntVar zero = makeIntVar(cp, 0, 0);
    CPIntVar one = makeIntVar(cp, 1, 1);
    CPIntVar four = makeIntVar(cp, 4, 4);

    // decision variables: grid[i][j] = 1 if the cell in row i, column j is alive
    CPBoolVar[][] grid = new CPBoolVar[n][cols];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < cols; j++)
        grid[i][j] = m.boolVar();

    // padded board: one ring of dead cells around the n x m active grid
    CPIntVar[][] board = new CPIntVar[n + 2][cols + 2];
    for (int r = 0; r < n + 2; r++)
      for (int c = 0; c < cols + 2; c++)
        board[r][c] = zero;
    for (int i = 0; i < n; i++)
      for (int j = 0; j < cols; j++)
        board[i + 1][j + 1] = grid[i][j];

    for (int r = 0; r < n + 2; r++) {
      for (int c = 0; c < cols + 2; c++) {
        // the live neighbours of this cell: the eight surrounding board cells
        java.util.List<CPIntVar> nbList = new java.util.ArrayList<>();
        for (int rr = r - 1; rr <= r + 1; rr++)
          for (int cc = c - 1; cc <= c + 1; cc++) {
            if (rr == r && cc == c) continue;
            if (rr < 0 || rr >= n + 2 || cc < 0 || cc >= cols + 2) continue;
            nbList.add(board[rr][cc]);
          }
        // a cell with fewer than three neighbours on the board can never have exactly three
        if (nbList.size() < 3) continue;
        CPIntVar live_neighbours = sum(nbList.toArray(new CPIntVar[0]));

        boolean isRing = r == 0 || r == n + 1 || c == 0 || c == cols + 1;
        if (isRing) {
          // a dead cell just outside the grid must not have exactly 3 live neighbours
          cp.post(neq(live_neighbours, 3));
          continue;
        }

        CPBoolVar alive = grid[r - 1][c - 1];
        // a dead cell must not have exactly 3 live neighbours (it would be born)
        CPBoolVar exactly_three = isEq(live_neighbours, 3);
        cp.post(or(new CPBoolVar[] {alive, not(exactly_three)}));
        // a live cell must have at least 2 live neighbours (it does not die of underpopulation)
        CPBoolVar at_most_one = isLe(live_neighbours, one);
        cp.post(implies(alive, not(at_most_one)));
        // a live cell must have at most 3 live neighbours (it does not die of overcrowding)
        CPBoolVar at_least_four = isLe(four, live_neighbours);
        cp.post(implies(alive, not(at_least_four)));
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
