import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;

// Golomb ruler: choose marks 0 = a_1 < a_2 < ... < a_m so that all differences
// a_j - a_i (i < j) are distinct, minimising the length a_m.
public class Submission {
    public static void build(Instance inst, Model m, Outputs out) {
        // the number of marks comes from the instance
        int n = inst.getInt("size");

        // a ruler of length n*n always exists for these sizes, so every mark fits in 0..n*n
        int upper = n * n;
        CPIntVar[] marks = m.intVarArray(n, 0, upper);

        // the first mark is at 0
        m.cp().post(eq(marks[0], 0));

        // the marks are strictly increasing
        m.cp().post(allDifferent(marks));
        for (int i = 0; i + 1 < n; i++) m.cp().post(le(marks[i], marks[i + 1]));

        // all the differences between two marks are distinct
        int pairs = n * (n - 1) / 2;
        CPIntVar[] differences = new CPIntVar[pairs];
        int p = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                // the difference a_j - a_i is the gap between mark i and mark j
                int k = j - i;
                CPIntVar gap = m.intVar(k * (k + 1) / 2, upper);
                m.cp().post(sum(new CPIntVar[]{marks[i], gap}, marks[j]));
                differences[p++] = gap;
            }
        }
        m.cp().post(allDifferent(differences));

        // k distinct differences add up to at least 1 + 2 + ... + k, so the marks are spread out
        for (int i = 0; i < n; i++) {
            int k = i;
            m.cp().post(ge(marks[i], k * (k + 1) / 2));
        }

        // the length of the ruler is the position of the last mark, to be minimised
        CPIntVar length = marks[n - 1];
        m.minimize(length);

        out.put("length", length);
        out.put("marks", marks);
    }
}
