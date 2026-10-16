import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.util.tools.ArrayUtils;
import dcp.Instance;
import dcp.Outputs;

// Vessel loading: place cuboid containers in a single layer on a rectangular deck, without
// overlap and with the minimum separation between container classes along or across the deck.
// Positions are 0-based edges: left and bottom are the lower edges of a container, right and top
// its upper edges (exclusive), so a container covers columns left..right-1 and rows bottom..top-1.
// Containers stay parallel to the deck sides but may be turned by 90 degrees.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int deckWidth = inst.getInt("deck_width");
    int deckLength = inst.getInt("deck_length");
    int n = inst.getInt("n_containers");
    int[] width = inst.getIntArray("width");
    int[] length = inst.getIntArray("length");
    int[] classes = inst.getIntArray("classes");
    int[][] separation = inst.getIntMatrix("separation"); // indexed by class - 1

    BoolVar[] turned = m.boolVarArray("turned", n);   // turned[i] = 1 if container i is rotated by 90 degrees
    IntVar[] left = new IntVar[n], right = new IntVar[n], bottom = new IntVar[n], top = new IntVar[n];
    IntVar[] extentX = new IntVar[n], extentY = new IntVar[n];
    for (int i = 0; i < n; i++) {
      int lo = Math.min(width[i], length[i]), hi = Math.max(width[i], length[i]);
      // extent along the deck width and along the deck length, depending on whether the container is turned
      extentX[i] = m.intVar("extent_x_" + i, lo, hi, true);
      extentY[i] = m.intVar("extent_y_" + i, lo, hi, true);
      m.element(extentX[i], new int[]{width[i], length[i]}, turned[i], 0).post();
      m.element(extentY[i], new int[]{length[i], width[i]}, turned[i], 0).post();

      left[i] = m.intVar("left_" + i, 0, deckWidth, true);
      right[i] = m.intVar("right_" + i, 0, deckWidth, true);
      bottom[i] = m.intVar("bottom_" + i, 0, deckLength, true);
      top[i] = m.intVar("top_" + i, 0, deckLength, true);
      // the container spans its extent along the deck width (left..right) and along the deck length (bottom..top)
      m.scalar(new IntVar[]{right[i], left[i], extentX[i]}, new int[]{1, -1, -1}, "=", 0).post();
      m.scalar(new IntVar[]{top[i], bottom[i], extentY[i]}, new int[]{1, -1, -1}, "=", 0).post();
    }

    // containers do not overlap on the deck (redundant with the pairwise separation below)
    m.diffN(left, bottom, extentX, extentY, true).post();

    // every pair of containers is separated in one of four ways, each with the class separation as the minimum gap
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        int sep = separation[classes[i] - 1][classes[j] - 1];
        // container j lies at least sep to the right of i, or i to the right of j, or sep above or below
        BoolVar iLeftOfJ = m.arithm(left[j], "-", right[i], ">=", sep).reify();
        BoolVar jLeftOfI = m.arithm(left[i], "-", right[j], ">=", sep).reify();
        BoolVar iBelowJ = m.arithm(bottom[j], "-", top[i], ">=", sep).reify();
        BoolVar jBelowI = m.arithm(bottom[i], "-", top[j], ">=", sep).reify();
        // containers i and j do not overlap, and are separated along or across the deck
        m.sum(new BoolVar[]{iLeftOfJ, jLeftOfI, iBelowJ, jBelowI}, ">=", 1).post();
      }
    }

    m.getSolver().setSearch(Search.domOverWDegSearch(ArrayUtils.append(turned, left, bottom)));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("left", left);
    out.put("right", right);
    out.put("top", top);
    out.put("bottom", bottom);
  }
}
