import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Farmer and cows: distribute the cows numbered 1..num_cows among num_sons sons so
// that each son gets the given number of cows and the same total quantity of milk.
// Cow c gives milk c, and the milk total is shared equally among the sons.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numCows = inst.getInt("num_cows");
    int numSons = inst.getInt("num_sons");
    int[] cowsPerSon = inst.getIntArray("cows_per_son");

    // gives[c][i] = 1 if cow c+1 goes to son i
    BoolVar[][] gives = m.boolVarMatrix("gives", numCows, numSons);

    // each cow goes to exactly one son, and the son is the cow_assignments output
    IntVar[] son = m.intVarArray("cow_assignments", numCows, 0, numSons - 1);
    for (int c = 0; c < numCows; c++) m.boolsIntChanneling(gives[c], son[c], 0).post();

    // each son gets the given number of cows
    for (int i = 0; i < numSons; i++) {
      BoolVar[] col = new BoolVar[numCows];
      for (int c = 0; c < numCows; c++) col[c] = gives[c][i];
      m.sum(col, "=", cowsPerSon[i]).post();
    }

    // the total milk is 1 + 2 + ... + num_cows, shared equally among the sons
    int totalMilk = numCows * (numCows + 1) / 2;
    int milkPerSon = totalMilk / numSons;

    // the milk of the cows given to each son is the same for every son
    int[] milk = new int[numCows];
    for (int c = 0; c < numCows; c++) milk[c] = c + 1;
    for (int i = 0; i < numSons; i++) {
      BoolVar[] col = new BoolVar[numCows];
      for (int c = 0; c < numCows; c++) col[c] = gives[c][i];
      m.scalar(col, milk, "=", milkPerSon).post();
    }

    // branch on the cows' Booleans, the cows with the largest milk first
    BoolVar[] order = new BoolVar[numCows * numSons];
    for (int c = numCows - 1, k = 0; c >= 0; c--)
      for (int i = 0; i < numSons; i++) order[k++] = gives[c][i];
    m.getSolver().setSearch(Search.inputOrderUBSearch(order));

    out.put("cow_assignments", son);
  }
}
