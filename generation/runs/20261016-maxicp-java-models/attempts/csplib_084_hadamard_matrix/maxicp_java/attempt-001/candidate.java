import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Hadamard matrix Legendre pairs: two sequences A = [a_1..a_l] and B = [b_1..b_l] over {-1, +1},
// with l odd and m = (l - 1) / 2.
public class Submission {

    // the table of x * y for x, y in {-1, +1}: rows are (x, y, x * y)
    private static final int[][] PRODUCT = {{-1, -1, 1}, {-1, 1, -1}, {1, -1, -1}, {1, 1, 1}};

    public static void build(Instance inst, Model m, Outputs out) {
        int l = inst.getInt("l");
        int mm = (l - 1) / 2;

        // the entries a_1..a_l and b_1..b_l are each -1 or +1
        CPIntVar[] a = signs(m, l);
        CPIntVar[] b = signs(m, l);

        // PAF(A, s) + PAF(B, s) = -2 for every s = 1..m, where PAF(A, s) = sum over i of a_i * a_{i+s}
        // (indices taken mod l)
        for (int s = 1; s <= mm; s++) {
            CPIntVar[] terms = new CPIntVar[2 * l];
            for (int i = 0; i < l; i++) {
                terms[i] = product(m, a[i], a[(i + s) % l]);
                terms[l + i] = product(m, b[i], b[(i + s) % l]);
            }
            m.cp().post(sum(terms, -2));
        }

        // a_1 + ... + a_l = 1
        m.cp().post(sum(a, 1));
        // b_1 + ... + b_l = 1
        m.cp().post(sum(b, 1));

        out.put("a", a);
        out.put("b", b);
    }

    // l variables with values in {-1, +1}
    private static CPIntVar[] signs(Model m, int l) {
        CPIntVar[] xs = m.intVarArray(l, -1, 1);
        for (CPIntVar x : xs) {
            // each entry is -1 or +1, never 0
            m.cp().post(neq(x, 0));
        }
        return xs;
    }

    // a fresh variable p equal to x * y, for x and y in {-1, +1}
    private static CPIntVar product(Model m, CPIntVar x, CPIntVar y) {
        CPIntVar p = m.intVar(-1, 1);
        m.cp().post(table(new CPIntVar[] {x, y, p}, PRODUCT));
        return p;
    }
}
