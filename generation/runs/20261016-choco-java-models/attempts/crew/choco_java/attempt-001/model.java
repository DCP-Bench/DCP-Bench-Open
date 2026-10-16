import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

// Crew assignment: give each of the 20 flight attendants a place on the 10 flights so that
// every flight has its required number of cabin crew, with the required stewards, hostesses
// and speakers of each language, and no attendant works one of the two flights after a flight they work.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // attributes[p] = {steward, hostess, French, Spanish, German} for attendant p (1 = has it)
    int[][] attributes = inst.getIntMatrix("attributes");
    // required[f] = {crew size, stewards, hostesses, French, Spanish, German} for flight f
    int[][] required = inst.getIntMatrix("required_crew");
    int flights = required.length;
    int people = attributes.length;

    // crew[f][p] = 1 if attendant p is assigned to flight f
    BoolVar[][] crew = m.boolVarMatrix("crew", flights, people);

    for (int f = 0; f < flights; f++) {
      // a flight needs a certain number of cabin crew
      m.sum(crew[f], "=", required[f][0]).post();

      // the flight needs at least the required number of stewards, hostesses and speakers of
      // each language; a person counts toward every role or language they have
      for (int k = 1; k <= 5; k++) {
        int attribute = k - 1;
        List<BoolVar> qualified = new ArrayList<>();
        for (int p = 0; p < people; p++) {
          if (attributes[p][attribute] == 1) qualified.add(crew[f][p]);
        }
        if (required[f][k] > 0) {
          m.sum(qualified.toArray(new BoolVar[0]), ">=", required[f][k]).post();
        }
      }
    }

    // every attendant who works a flight has the two flights after it off
    for (int p = 0; p < people; p++) {
      for (int f = 0; f < flights; f++) {
        for (int gap = 1; gap <= 2 && f + gap < flights; gap++) {
          m.arithm(crew[f][p], "+", crew[f + gap][p], "<=", 1).post();
        }
      }
    }

    // the output is satisfaction only, so there is no objective
    out.put("crew", crew);
  }
}
