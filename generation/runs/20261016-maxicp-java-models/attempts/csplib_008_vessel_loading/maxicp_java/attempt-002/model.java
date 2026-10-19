// Vessel loading: place cuboid containers, laid out in a single layer and parallel
// to the sides of a rectangular deck, without overlap and so that containers of
// separated classes are at least the required distance apart along or across the deck.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_containers");
    int deckWidth = inst.getInt("deck_width");
    int deckLength = inst.getInt("deck_length");
    int[] width = inst.getIntArray("width");
    int[] length = inst.getIntArray("length");
    int[] classes = inst.getIntArray("classes");
    int[][] separation = inst.getIntMatrix("separation");

    // a container may be turned by a quarter turn, which swaps its width and length
    CPBoolVar[] turned = m.boolVarArray(n);

    // the footprint of container i along the deck width and along the deck length
    CPIntVar[] alongWidth = new CPIntVar[n];
    CPIntVar[] alongLength = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      alongWidth[i] = element(new int[] { width[i], length[i] }, turned[i]);
      alongLength[i] = element(new int[] { length[i], width[i] }, turned[i]);
    }

    // every container lies on the deck
    CPIntVar[] left = m.intVarArray(n, 0, deckWidth);
    CPIntVar[] right = m.intVarArray(n, 0, deckWidth);
    CPIntVar[] bottom = m.intVarArray(n, 0, deckLength);
    CPIntVar[] top = m.intVarArray(n, 0, deckLength);
    for (int i = 0; i < n; i++) {
      // right edge = left edge + footprint along the width
      m.cp().post(sum(new CPIntVar[] { left[i], alongWidth[i] }, right[i]));
      // top edge = bottom edge + footprint along the length
      m.cp().post(sum(new CPIntVar[] { bottom[i], alongLength[i] }, top[i]));
    }

    // containers do not overlap, and containers of separated classes keep their
    // minimum distance either along the deck or across the deck
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        int ci = classes[i] - 1;
        int cj = classes[j] - 1;
        int gap = Math.max(separation[ci][cj], separation[cj][ci]);
        // neg[k] = 1 means relation k is not used; once the positions are fixed,
        // propagation fixes these, so the search does not branch on them
        CPBoolVar[] neg = makeBoolVarArray(m.cp(), 4);
        m.cp().post(eq(neg[0], not(isLe(plus(right[i], gap), left[j]))));
        m.cp().post(eq(neg[1], not(isLe(plus(right[j], gap), left[i]))));
        m.cp().post(eq(neg[2], not(isLe(plus(top[i], gap), bottom[j]))));
        m.cp().post(eq(neg[3], not(isLe(plus(top[j], gap), bottom[i]))));
        // at least one of the four relations holds
        m.cp().post(le(sum(neg), 3));
      }
    }

    out.put("left", left);
    out.put("right", right);
    out.put("bottom", bottom);
    out.put("top", top);
  }
}
