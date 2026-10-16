import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Perfect square placement: pack squares with the given integer sides into a
// square of side base so that no two squares overlap, all borders are parallel
// to the border of the big square, and the squares cover it with no spare space.
// Coordinates start from 0.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int base = inst.getInt("base");
    int[] sides = inst.getIntArray("sides");
    int n = sides.length;

    // the squares' surfaces add up to the surface of the packing square (no spare capacity)
    int area = 0;
    for (int s : sides) area += s * s;
    if (area != base * base) throw new IllegalArgumentException("square areas do not sum to base^2");

    // each square lies inside the packing square: coordinates run from 0 to base - side
    IntVar[] x = new IntVar[n];
    IntVar[] y = new IntVar[n];
    IntVar[] w = new IntVar[n];
    IntVar[] h = new IntVar[n];
    for (int i = 0; i < n; i++) {
      x[i] = m.intVar("x" + i, 0, base - sides[i], true);
      y[i] = m.intVar("y" + i, 0, base - sides[i], true);
      w[i] = m.intVar(sides[i]);
      h[i] = m.intVar(sides[i]);
    }

    // the squares do not overlap each other, with borders parallel to the big square
    m.diffN(x, y, w, h, true).post();

    // redundant: at any column, the squares crossing it fit within the base width
    m.cumulative(x, sides, sides, base).post();
    // redundant: at any row, the squares crossing it fit within the base height
    m.cumulative(y, sides, sides, base).post();

    // branch on all coordinates with dom/wdeg, which learns from failures; Luby restarts
    IntVar[] coords = new IntVar[2 * n];
    for (int i = 0; i < n; i++) {
      coords[i] = x[i];
      coords[n + i] = y[i];
    }
    m.getSolver().setSearch(Search.domOverWDegSearch(coords));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("x_coords", x);
    out.put("y_coords", y);
  }
}
