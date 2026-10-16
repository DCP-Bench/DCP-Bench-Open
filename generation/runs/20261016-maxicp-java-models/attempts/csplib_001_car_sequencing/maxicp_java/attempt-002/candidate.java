// Car sequencing: a number of cars of several types must be arranged on an
// assembly line so that each option station is never over capacity.
// Output: sequence[p] is the car type (0-based) at position p.

import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] demand = inst.getIntArray("demand");       // cars wanted of each type
    int[] atMost = inst.getIntArray("at_most");       // capacity of each station
    int[] perSlots = inst.getIntArray("per_slots");   // window length of each station
    int[][] requires = inst.getIntMatrix("requires"); // requires[type][option]

    int numTypes = demand.length;
    int numOptions = atMost.length;
    int numCars = 0;
    for (int d : demand) numCars += d;

    // the sequence: position p holds car type seq[p]. It is the only registered
    // decision variable, so the search fixes the sequence and every quantity
    // below follows from it through the table constraints.
    CPIntVar[] seq = m.intVarArray(numCars, 0, numTypes - 1);

    // typeOf[p][t] is 1 when position p holds type t; needs[p][o] is 1 when the
    // car at position p requires option o. Unregistered, so not branched on.
    CPBoolVar[][] typeOf = new CPBoolVar[numCars][numTypes];
    CPBoolVar[][] needs = new CPBoolVar[numCars][numOptions];

    // one row per car type ties the position's type to its one-hot flags and
    // to the options that type requires, so the flags stay consistent with the
    // sequence on every propagation
    int width = 1 + numTypes + numOptions;
    int[][] rows = new int[numTypes][width];
    for (int t = 0; t < numTypes; t++) {
      rows[t][0] = t;
      rows[t][1 + t] = 1;
      for (int o = 0; o < numOptions; o++) rows[t][1 + numTypes + o] = requires[t][o];
    }
    for (int p = 0; p < numCars; p++) {
      CPIntVar[] cols = new CPIntVar[width];
      cols[0] = seq[p];
      for (int t = 0; t < numTypes; t++) {
        typeOf[p][t] = makeBoolVar(m.cp());
        cols[1 + t] = typeOf[p][t];
      }
      for (int o = 0; o < numOptions; o++) {
        needs[p][o] = makeBoolVar(m.cp());
        cols[1 + numTypes + o] = needs[p][o];
      }
      m.cp().post(table(cols, rows));
    }

    // the number of cars of each type is its demand
    for (int t = 0; t < numTypes; t++) {
      CPBoolVar[] holdsType = new CPBoolVar[numCars];
      for (int p = 0; p < numCars; p++) holdsType[p] = typeOf[p][t];
      m.cp().post(sum(holdsType, demand[t]));
    }

    for (int o = 0; o < numOptions; o++) {
      // the whole line needs this option as often as the demanded cars do
      int totalNeeds = 0;
      for (int t = 0; t < numTypes; t++) totalNeeds += demand[t] * requires[t][o];
      CPBoolVar[] needsOption = new CPBoolVar[numCars];
      for (int p = 0; p < numCars; p++) needsOption[p] = needs[p][o];
      m.cp().post(sum(needsOption, totalNeeds));

      // a station handles at most at_most cars in any per_slots consecutive cars
      int window = perSlots[o];
      for (int start = 0; start + window <= numCars; start++) {
        CPIntVar[] inWindow = new CPIntVar[window];
        for (int k = 0; k < window; k++) inWindow[k] = needs[start + k][o];
        m.cp().post(le(sum(inWindow), atMost[o]));
        // the cars before and after this window are covered by the fewest
        // windows of the same length that stay inside the line; each holds at
        // most at_most, so this window holds at least the rest of the needs
        int before = (start + window - 1) / window;
        int after = (numCars - start - window + window - 1) / window;
        int minInWindow = totalNeeds - (before + after) * atMost[o];
        if (minInWindow > 0) m.cp().post(ge(sum(inWindow), minInWindow));
      }
    }

    out.put("sequence", seq);
  }
}
