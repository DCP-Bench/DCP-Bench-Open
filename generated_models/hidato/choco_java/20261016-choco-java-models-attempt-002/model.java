import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Hidato: fill an R x C grid with the numbers 1..R*C so that consecutive numbers touch
// horizontally, vertically or diagonally, keeping the numbers given in the puzzle.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] puzzle = inst.getIntMatrix("puzzle");  // 0 = empty cell
    int rows = puzzle.length, cols = puzzle[0].length;
    int cells = rows * cols;                       // the numbers are 1..cells

    // value[p] = number (0-based, so number - 1) in the cell with flat index p = r * cols + c
    IntVar[] value = m.intVarArray("value", cells, 0, cells - 1);
    // pos[v] = flat index of the cell holding number v + 1
    IntVar[] pos = m.intVarArray("pos", cells, 0, cells - 1);

    // the two arrays describe the same placement: every number in exactly one cell
    m.inverseChanneling(value, pos).post();

    // the numbers given in the puzzle keep their cells
    for (int r = 0; r < rows; r++)
      for (int c = 0; c < cols; c++)
        if (puzzle[r][c] != 0) m.arithm(pos[puzzle[r][c] - 1], "=", r * cols + c).post();

    // allowed cell pairs for two touching cells: horizontal, vertical or diagonal neighbours
    Tuples touching = new Tuples(true);
    for (int r = 0; r < rows; r++)
      for (int c = 0; c < cols; c++)
        for (int dr = -1; dr <= 1; dr++)
          for (int dc = -1; dc <= 1; dc++) {
            int r2 = r + dr, c2 = c + dc;
            if ((dr == 0 && dc == 0) || r2 < 0 || r2 >= rows || c2 < 0 || c2 >= cols) continue;
            touching.add(r * cols + c, r2 * cols + c2);
          }

    // number v and number v + 1 sit in touching cells
    for (int v = 0; v + 1 < cells; v++)
      m.table(new IntVar[]{pos[v], pos[v + 1]}, touching).post();

    // output the grid: x[r][c] = number in cell (r, c)
    IntVar[][] x = new IntVar[rows][cols];
    for (int r = 0; r < rows; r++)
      for (int c = 0; c < cols; c++)
        x[r][c] = m.offset(value[r * cols + c], 1);

    out.put("x", x);
  }
}
