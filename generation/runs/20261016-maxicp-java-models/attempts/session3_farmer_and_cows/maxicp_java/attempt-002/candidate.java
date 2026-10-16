import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// A farmer has cows numbered 1 up to num_cows; cow i gives i litres of milk.
// He has num_sons sons and gives son s exactly cows_per_son[s] cows.
// The total milk each son gets must be the same.
// cow_assignments[i] is the son (0-based) that cow i+1 goes to.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numCows = inst.getInt("num_cows");
    int numSons = inst.getInt("num_sons");
    int[] cowsPerSon = inst.getIntArray("cows_per_son");

    // one decision Boolean per cow and son: notGiven[i][s] is false when cow i+1 goes to son s
    // made son by son, largest cow first; the search tries giving a cow before not giving it
    CPBoolVar[][] notGiven = new CPBoolVar[numCows][numSons];
    for (int s = 0; s < numSons; s++)
      for (int i = numCows - 1; i >= 0; i--)
        notGiven[i][s] = m.boolVar();

    // x[i][s] is 1 when cow i+1 goes to son s
    CPIntVar[][] x = new CPIntVar[numCows][numSons];
    for (int i = 0; i < numCows; i++)
      for (int s = 0; s < numSons; s++)
        x[i][s] = not(notGiven[i][s]);

    // every cow goes to exactly one son
    for (int i = 0; i < numCows; i++)
      m.cp().post(eq(sum(x[i]), 1));

    // each son gets the number of cows given in the distribution
    for (int s = 0; s < numSons; s++) {
      CPIntVar[] onSon = new CPIntVar[numCows];
      for (int i = 0; i < numCows; i++) onSon[i] = x[i][s];
      m.cp().post(eq(sum(onSon), cowsPerSon[s]));
    }

    // the total milk is the sum of the cow numbers 1 to num_cows, shared equally among the sons
    long total = (long) numCows * (numCows + 1) / 2;
    if (total % numSons != 0) throw new InconsistencyException();
    int milkPerSon = (int) (total / numSons);

    // every son gets the same total milk, where cow i+1 gives i+1 litres
    for (int s = 0; s < numSons; s++) {
      CPIntVar[] milk = new CPIntVar[numCows];
      for (int i = 0; i < numCows; i++) milk[i] = mul(x[i][s], i + 1);
      m.cp().post(eq(sum(milk), milkPerSon));
    }

    // the son of each cow is the output: the index of the one son it goes to
    CPIntVar[] cow = new CPIntVar[numCows];
    for (int i = 0; i < numCows; i++) {
      CPIntVar[] sonOf = new CPIntVar[numSons];
      for (int s = 0; s < numSons; s++) sonOf[s] = mul(x[i][s], s);
      cow[i] = sum(sonOf);
    }
    out.put("cow_assignments", cow);
  }
}
