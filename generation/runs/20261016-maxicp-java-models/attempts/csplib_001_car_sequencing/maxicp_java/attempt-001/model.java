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

    // each position holds exactly one car type: isType[p][t] says position p holds type t
    CPIntVar[] seq = m.intVarArray(numCars, 0, numTypes - 1);
    CPBoolVar[][] isType = new CPBoolVar[numCars][];
    for (int p = 0; p < numCars; p++) {
      // the search branches on absent[p][t] first, so it tries a type present before absent
      CPBoolVar[] absent = m.boolVarArray(numTypes);
      isType[p] = new CPBoolVar[numTypes];
      for (int t = 0; t < numTypes; t++) isType[p][t] = not(absent[t]);
      m.cp().post(eq(sum(isType[p]), 1));
      // the sequence value at p is the type that holds there
      CPIntVar[] scaled = new CPIntVar[numTypes];
      for (int t = 0; t < numTypes; t++) scaled[t] = mul(isType[p][t], t);
      m.cp().post(eq(sum(scaled), seq[p]));
    }

    // the number of cars of each type is its demand
    for (int t = 0; t < numTypes; t++) {
      CPBoolVar[] holdsType = new CPBoolVar[numCars];
      for (int p = 0; p < numCars; p++) holdsType[p] = isType[p][t];
      m.cp().post(eq(sum(holdsType), demand[t]));
    }

    // a station handles at most at_most cars in any per_slots consecutive cars
    for (int o = 0; o < numOptions; o++) {
      // needs[p] is 1 when the car at position p requires this option
      CPIntVar[] needs = new CPIntVar[numCars];
      for (int p = 0; p < numCars; p++) {
        CPIntVar[] terms = new CPIntVar[numTypes];
        for (int t = 0; t < numTypes; t++) terms[t] = mul(isType[p][t], requires[t][o]);
        needs[p] = sum(terms);
      }
      // the whole line needs this option as often as the demanded cars do
      int totalNeeds = 0;
      for (int t = 0; t < numTypes; t++) totalNeeds += demand[t] * requires[t][o];
      m.cp().post(eq(sum(needs), totalNeeds));
      int window = perSlots[o];
      for (int start = 0; start + window <= numCars; start++) {
        CPIntVar[] inWindow = new CPIntVar[window];
        for (int k = 0; k < window; k++) inWindow[k] = needs[start + k];
        m.cp().post(le(sum(inWindow), atMost[o]));
      }
    }

    out.put("sequence", seq);
  }
}
