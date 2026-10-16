import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Solitaire battleships: place the fleet on the grid so that the row and column counts of
// occupied squares, the fleet composition and the shots all hold, with no two ships touching.
public class Submission {
  // a ship placement: the cells it covers, in order, and its length
  static class Placement {
    final int[][] cells;
    final boolean horizontal;
    final BoolVar used;
    Placement(int[][] cells, boolean horizontal, BoolVar used) {
      this.cells = cells;
      this.horizontal = horizontal;
      this.used = used;
    }
  }

  public static void build(Instance inst, Model m, Outputs out) {
    int rows = inst.getInt("rows");
    int cols = inst.getInt("cols");
    int[] rowsum = inst.getIntArray("rowsum");
    int[] colsum = inst.getIntArray("colsum");
    int[][] fleet = inst.getIntMatrix("fleet_counts");   // rows of {length, number of ships}
    int[][] hints = inst.getIntMatrix("hints");           // rows of {row, col, code}

    // the cell codes, as this instance names them
    int water = inst.getInt("WATER");
    int circle = inst.getInt("CIRCLE");
    int left = inst.getInt("LEFT");
    int right = inst.getInt("RIGHT");
    int top = inst.getInt("TOP");
    int bottom = inst.getInt("BOTTOM");
    int middle = inst.getInt("MIDDLE");
    int[] codes = {water, circle, left, right, top, bottom, middle};

    // grid[r][c]: the code of the cell: water, submarine, or one part of a ship
    IntVar[][] grid = new IntVar[rows][cols];
    BoolVar[][] occ = new BoolVar[rows][cols];   // occ[r][c] = 1 when a vessel is on the cell
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        grid[r][c] = m.intVar("cell_" + r + "_" + c, codes);
        occ[r][c] = grid[r][c].ne(water).boolVar();
      }
    }

    // every ship position of each length: horizontal and vertical, and a submarine per cell
    List<Placement> all = new ArrayList<>();
    List<List<Placement>> byLength = new ArrayList<>();
    for (int len = 1; len <= 4; len++) {
      List<Placement> ofLen = new ArrayList<>();
      for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
          if (len == 1) {
            ofLen.add(placement(m, new int[][]{{r, c}}, false, "sub", r, c, all));
            continue;
          }
          if (c + len <= cols) {
            int[][] cells = new int[len][];
            for (int k = 0; k < len; k++) cells[k] = new int[]{r, c + k};
            ofLen.add(placement(m, cells, true, "h" + len, r, c, all));
          }
          if (r + len <= rows) {
            int[][] cells = new int[len][];
            for (int k = 0; k < len; k++) cells[k] = new int[]{r + k, c};
            ofLen.add(placement(m, cells, false, "v" + len, r, c, all));
          }
        }
      }
      byLength.add(ofLen);
    }

    // each ship position counts as used, and its cells take the codes of a ship part
    for (int len = 1; len <= 4; len++) {
      for (Placement p : byLength.get(len - 1)) {
        int n = p.cells.length;
        for (int k = 0; k < n; k++) {
          int r = p.cells[k][0], c = p.cells[k][1];
          int code;
          if (len == 1) code = circle;
          else if (p.horizontal) code = (k == 0) ? left : (k == n - 1) ? right : middle;
          else code = (k == 0) ? top : (k == n - 1) ? bottom : middle;
          m.ifThen(m.arithm(p.used, "=", 1), m.arithm(grid[r][c], "=", code));
        }
        // a used ship has no other vessel on any of its neighbouring squares, even diagonally
        for (int[] nb : neighbours(p.cells, rows, cols)) {
          m.arithm(p.used, "+", occ[nb[0]][nb[1]], "<=", 1).post();
        }
      }
    }

    // every occupied square is covered by exactly one used ship, and water is covered by none
    List<List<BoolVar>> covering = new ArrayList<>();
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) covering.add(new ArrayList<>());
    }
    for (Placement p : all) {
      for (int[] cell : p.cells) covering.get(cell[0] * cols + cell[1]).add(p.used);
    }
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        List<BoolVar> cov = covering.get(r * cols + c);
        m.sum(cov.toArray(new BoolVar[0]), "=", occ[r][c]).post();
      }
    }

    // the fleet: the number of ships of each length
    for (int[] f : fleet) {
      int len = f[0], count = f[1];
      List<BoolVar> ofLen = new ArrayList<>();
      for (Placement p : byLength.get(len - 1)) ofLen.add(p.used);
      m.sum(ofLen.toArray(new BoolVar[0]), "=", count).post();
    }

    // the number of occupied squares in each row and column
    for (int r = 0; r < rows; r++) {
      m.sum(occ[r], "=", rowsum[r]).post();
    }
    for (int c = 0; c < cols; c++) {
      BoolVar[] column = new BoolVar[rows];
      for (int r = 0; r < rows; r++) column[r] = occ[r][c];
      m.sum(column, "=", colsum[c]).post();
    }

    // the shots: squares whose code is given
    for (int[] h : hints) {
      m.arithm(grid[h[0]][h[1]], "=", h[2]).post();
    }

    // branch on the ship positions
    BoolVar[] branch = new BoolVar[all.size()];
    for (int i = 0; i < all.size(); i++) branch[i] = all.get(i).used;
    IntVar[] cells = new IntVar[rows * cols];
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) cells[r * cols + c] = grid[r][c];
    }
    m.getSolver().setSearch(
        Search.minDomLBSearch(cells),
        Search.minDomLBSearch(branch));

    out.put("grid", grid);
  }

  // record a ship position and return it
  private static Placement placement(Model m, int[][] cells, boolean horizontal,
                                     String name, int r, int c, List<Placement> all) {
    BoolVar used = m.boolVar(name + "_" + r + "_" + c);
    Placement p = new Placement(cells, horizontal, used);
    all.add(p);
    return p;
  }

  // the squares around a ship, including diagonals, that are not part of the ship
  private static List<int[]> neighbours(int[][] cells, int rows, int cols) {
    List<int[]> out = new ArrayList<>();
    for (int[] cell : cells) {
      for (int dr = -1; dr <= 1; dr++) {
        for (int dc = -1; dc <= 1; dc++) {
          int r = cell[0] + dr, c = cell[1] + dc;
          if (r < 0 || c < 0 || r >= rows || c >= cols) continue;
          boolean inShip = false;
          for (int[] other : cells) {
            if (other[0] == r && other[1] == c) inShip = true;
          }
          if (!inShip) out.add(new int[]{r, c});
        }
      }
    }
    return out;
  }
}
