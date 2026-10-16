// Solitaire Battleships: fill a rows x cols grid with water and ships.
// Ships are straight horizontal or vertical lines of cells. The fleet is given by
// fleet_counts: [length, how many]. No two ships touch, not even diagonally.
// rowsum and colsum give how many cells of each row and column hold a vessel.
// Each cell is water, a submarine (one-cell ship), or a ship part: left, right,
// top, bottom or middle. Hints fix the content of some cells.
import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {

  // one possible ship: its boolean (1 = this ship is in the solution), its length,
  // and the cell and content it would put on each of its squares
  record Ship(CPBoolVar on, int len, int[] rows, int[] cols, int[] codes) {}

  public static void build(Instance inst, Model m, Outputs out) {
    int rows = inst.getInt("rows");
    int cols = inst.getInt("cols");
    int water = inst.getInt("WATER");
    int circle = inst.getInt("CIRCLE");
    int left = inst.getInt("LEFT");
    int right = inst.getInt("RIGHT");
    int top = inst.getInt("TOP");
    int bottom = inst.getInt("BOTTOM");
    int middle = inst.getInt("MIDDLE");
    int[] rowSum = inst.getIntArray("rowsum");
    int[] colSum = inst.getIntArray("colsum");
    int[][] fleet = inst.getIntMatrix("fleet_counts");
    int[][] hints = inst.has("hints") ? inst.getIntMatrix("hints") : new int[0][];
    var cp = m.cp();

    // the grid values a cell can take
    int lo = Math.min(water, Math.min(circle, Math.min(left, Math.min(right, Math.min(top, Math.min(bottom, middle))))));
    int hi = Math.max(water, Math.max(circle, Math.max(left, Math.max(right, Math.max(top, Math.max(bottom, middle))))));

    // every ship of every length in the fleet, horizontal or vertical
    // (a one-cell ship is listed once, since both orientations are the same)
    List<Ship> ships = new ArrayList<>();
    for (int[] f : fleet) {
      int len = f[0];
      int orientations = len == 1 ? 1 : 2;
      for (int o = 0; o < orientations; o++) {
        int dr = o == 0 ? 0 : 1;   // o = 0 horizontal, 1 vertical
        int dc = o == 0 ? 1 : 0;
        for (int r = 0; r + dr * (len - 1) < rows; r++) {
          for (int c = 0; c + dc * (len - 1) < cols; c++) {
            int[] sr = new int[len], sc = new int[len], code = new int[len];
            for (int i = 0; i < len; i++) {
              sr[i] = r + dr * i;
              sc[i] = c + dc * i;
              if (len == 1) code[i] = circle;
              else if (i == 0) code[i] = o == 0 ? left : top;
              else if (i == len - 1) code[i] = o == 0 ? right : bottom;
              else code[i] = middle;
            }
            ships.add(new Ship(m.boolVar(), len, sr, sc, code));
          }
        }
      }
    }

    // which ships cover each cell
    List<List<CPIntVar>> covering = new ArrayList<>();
    for (int i = 0; i < rows * cols; i++) covering.add(new ArrayList<>());
    for (Ship s : ships)
      for (int i = 0; i < s.len(); i++)
        covering.get(s.rows()[i] * cols + s.cols()[i]).add(s.on());

    // the fleet: exactly fleet_counts[k][1] ships of length fleet_counts[k][0]
    for (int[] f : fleet) {
      List<CPIntVar> ofLength = new ArrayList<>();
      for (Ship s : ships) if (s.len() == f[0]) ofLength.add(s.on());
      if (!ofLength.isEmpty())
        cp.post(eq(sum(ofLength.toArray(new CPIntVar[0])), f[1]));
    }

    // no two ships touch, not even diagonally: two different ships may not
    // occupy squares that are equal or next to each other in any direction
    for (int a = 0; a < ships.size(); a++) {
      for (int b = a + 1; b < ships.size(); b++) {
        if (touch(ships.get(a), ships.get(b)))
          cp.post(le(sum(new CPIntVar[] {ships.get(a).on(), ships.get(b).on()}), 1));
      }
    }

    // a cell holds a vessel exactly when a ship covers it (at most one can, see above)
    CPIntVar[] occupied = new CPIntVar[rows * cols];
    for (int i = 0; i < rows * cols; i++) {
      List<CPIntVar> cover = covering.get(i);
      occupied[i] = cover.isEmpty() ? m.intVar(0, 0) : sum(cover.toArray(new CPIntVar[0]));
    }

    // the cell content: the content of the ship covering it, or water
    CPIntVar[][] grid = new CPIntVar[rows][cols];
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        grid[r][c] = m.intVar(lo, hi);
        List<CPIntVar> parts = new ArrayList<>();
        for (Ship s : ships)
          for (int i = 0; i < s.len(); i++)
            if (s.rows()[i] == r && s.cols()[i] == c)
              parts.add(mul(s.on(), s.codes()[i] - water));
        if (parts.isEmpty()) cp.post(eq(grid[r][c], water));
        else cp.post(eq(sum(parts.toArray(new CPIntVar[0])), minus(grid[r][c], water)));
      }
    }

    // rowsum: the number of vessel squares in each row
    for (int r = 0; r < rows; r++) {
      CPIntVar[] row = new CPIntVar[cols];
      for (int c = 0; c < cols; c++) row[c] = occupied[r * cols + c];
      cp.post(eq(sum(row), rowSum[r]));
    }

    // colsum: the number of vessel squares in each column
    for (int c = 0; c < cols; c++) {
      CPIntVar[] column = new CPIntVar[rows];
      for (int r = 0; r < rows; r++) column[r] = occupied[r * cols + c];
      cp.post(eq(sum(column), colSum[c]));
    }

    // hints: the square at [row, col] has the content given by the hint's code
    for (int[] h : hints) cp.post(eq(grid[h[0]][h[1]], h[2]));

    out.put("grid", grid);
  }

  // two ships touch when some square of one is equal to or next to some square of the other
  static boolean touch(Ship a, Ship b) {
    for (int i = 0; i < a.len(); i++)
      for (int j = 0; j < b.len(); j++)
        if (Math.abs(a.rows()[i] - b.rows()[j]) <= 1 && Math.abs(a.cols()[i] - b.cols()[j]) <= 1)
          return true;
    return false;
  }
}
