import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Hadamard matrix Legendre pairs: find two sequences A and B of l entries, each -1 or +1,
// whose periodic autocorrelations add up to -2 at every shift s = 1..m, where m = (l-1)/2,
// with the entries of A summing to 1 and the entries of B summing to 1.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int l = inst.getInt("l");                 // length of each sequence, odd
    int half = (l - 1) / 2;                   // number of shifts, m

    IntVar[] a = new IntVar[l];
    IntVar[] b = new IntVar[l];
    for (int i = 0; i < l; i++) {
      a[i] = m.intVar("a" + i, new int[]{-1, 1});
      b[i] = m.intVar("b" + i, new int[]{-1, 1});
    }

    // for each shift s, the periodic autocorrelations of A and B at s sum to -2
    for (int s = 1; s <= half; s++) {
      IntVar[] products = new IntVar[2 * l];
      for (int i = 0; i < l; i++) {
        int j = (i + s) % l;                  // periodic index, i + s taken mod l
        products[i] = m.intVar("pa" + s + "_" + i, new int[]{-1, 1});
        m.times(a[i], a[j], products[i]).post();
        products[l + i] = m.intVar("pb" + s + "_" + i, new int[]{-1, 1});
        m.times(b[i], b[j], products[l + i]).post();
      }
      // PAF(A, s) + PAF(B, s) = -2
      m.sum(products, "=", -2).post();
    }

    // the entries of A sum to 1
    m.sum(a, "=", 1).post();

    // the entries of B sum to 1
    m.sum(b, "=", 1).post();

    IntVar[] all = new IntVar[2 * l];
    System.arraycopy(a, 0, all, 0, l);
    System.arraycopy(b, 0, all, l, l);
    m.getSolver().setSearch(Search.minDomLBSearch(all));

    out.put("a", a);
    out.put("b", b);
  }
}
