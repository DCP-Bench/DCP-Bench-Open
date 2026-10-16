// Ages of three sons: the product of the ages is 36; the sum of the ages equals
// the number of windows (not given, so it is a free variable); after the sum
// the mathematician still needs more information; then the oldest son is named
// and the mathematician knows the ages. Ages are reported starting from the oldest.

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.maxicp.cp.engine.core.CPIntVar;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import static org.maxicp.cp.CPFactory.*;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // The old man's first statement: the product of the three ages is 36.
    // Ages are whole numbers from 1 to 36, since no son is older than the product.
    CPIntVar a1 = m.intVar(1, 36);
    CPIntVar a2 = m.intVar(1, 36);
    CPIntVar a3 = m.intVar(1, 36);

    // Starting from the oldest: A1 >= A2 >= A3.
    m.cp().post(ge(a1, a2));
    m.cp().post(ge(a2, a3));

    // Enumerate the age triples (oldest first) whose product is 36. These are
    // constants of the puzzle, derived from the number 36, not from the instance.
    List<int[]> triples = new ArrayList<>();
    for (int x = 1; x <= 36; x++)
      for (int y = 1; y <= x; y++)
        for (int z = 1; z <= y; z++)
          if (x * y * z == 36) triples.add(new int[] {x, y, z});

    // The product of their ages is 36: (A1, A2, A3) is one of those triples.
    int[][] productRows = triples.toArray(new int[0][]);
    m.cp().post(table(new CPIntVar[] {a1, a2, a3}, productRows));

    // The sum of the ages equals the number of windows. The mathematician needs
    // more information after hearing the sum, so the sum must be shared by at
    // least two of the triples above. Count the triples for each sum.
    Map<Integer, Integer> triplesWithSum = new HashMap<>();
    for (int[] t : triples) triplesWithSum.merge(t[0] + t[1] + t[2], 1, Integer::sum);
    List<int[]> ambiguousSums = new ArrayList<>();
    for (Map.Entry<Integer, Integer> e : triplesWithSum.entrySet())
      if (e.getValue() >= 2) ambiguousSums.add(new int[] {e.getKey()});

    // The number of windows is the sum of the ages, and it is one of the ambiguous sums.
    CPIntVar windows = m.intVar(3, 108);
    m.cp().post(eq(sum(new CPIntVar[] {a1, a2, a3}), windows));
    m.cp().post(table(new CPIntVar[] {windows}, ambiguousSums.toArray(new int[0][])));

    // The oldest son has blue eyes, so there is one oldest son: A1 is strictly older than A2.
    m.cp().post(ge(a1, plus(a2, 1)));

    out.put("A1", a1);
    out.put("A2", a2);
    out.put("A3", a3);
  }
}
