import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Crew: assign the flight attendants to the flights. Each flight needs a number
// of cabin crew who speak the required languages, and after an attended flight
// a cabin crew member has two flights off.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] attributes = inst.getIntMatrix("attributes");   // per attendant: steward, hostess, French, Spanish, German
    int[][] required = inst.getIntMatrix("required_crew");  // per flight: crew size, stewards, hostesses, French, Spanish, German
    int nPeople = attributes.length;
    int nFlights = required.length;

    // crew[f][p] = 1 if attendant p is assigned to flight f
    CPBoolVar[][] crew = new CPBoolVar[nFlights][];
    for (int f = 0; f < nFlights; f++) {
      crew[f] = m.boolVarArray(nPeople);
    }

    for (int f = 0; f < nFlights; f++) {
      // each flight needs the stated number of cabin crew
      CPIntVar[] onFlight = asInts(crew[f]);
      m.cp().post(eq(sum(onFlight), required[f][0]));

      // each flight needs the stated number of stewards, hostesses and speakers of
      // each language (at least that many)
      for (int c = 0; c < 5; c++) {
        int need = required[f][c + 1];
        if (need == 0) {
          continue;
        }
        CPIntVar[] qualified = new CPIntVar[nPeople];
        int count = 0;
        for (int p = 0; p < nPeople; p++) {
          if (attributes[p][c] == 1) {
            qualified[count++] = crew[f][p];
          }
        }
        CPIntVar[] chosen = new CPIntVar[count];
        System.arraycopy(qualified, 0, chosen, 0, count);
        m.cp().post(ge(sum(chosen), need));
      }
    }

    // after working a flight, a cabin crew member has the next two flights off
    for (int f = 0; f < nFlights; f++) {
      for (int p = 0; p < nPeople; p++) {
        for (int g = f + 1; g <= f + 2 && g < nFlights; g++) {
          m.cp().post(implies(crew[f][p], not(crew[g][p])));
        }
      }
    }

    out.put("crew", crew);
  }

  private static CPIntVar[] asInts(CPBoolVar[] bs) {
    CPIntVar[] xs = new CPIntVar[bs.length];
    for (int i = 0; i < bs.length; i++) {
      xs[i] = bs[i];
    }
    return xs;
  }
}
