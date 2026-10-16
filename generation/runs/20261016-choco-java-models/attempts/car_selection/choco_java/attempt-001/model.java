import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Car selection: assign participants to cars, each participant to at most one car and
// each car to at most one participant, only where the participant is interested in the car,
// maximising the total number of assignments.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] possible = inst.getIntMatrix("possible_assignments");
    int nParticipants = possible.length;
    int nCars = possible[0].length;

    // assignments[i][j]: 1 if participant i is assigned to car j
    BoolVar[][] assignments = new BoolVar[nParticipants][nCars];
    for (int i = 0; i < nParticipants; i++) {
      for (int j = 0; j < nCars; j++) {
        assignments[i][j] = m.boolVar("assign_" + i + "_" + j);
      }
    }

    // a participant is only assigned to a car the participant is interested in
    for (int i = 0; i < nParticipants; i++) {
      for (int j = 0; j < nCars; j++) {
        if (possible[i][j] == 0) {
          m.arithm(assignments[i][j], "=", 0).post();
        }
      }
    }

    // each participant is assigned to at most one car
    for (int i = 0; i < nParticipants; i++) {
      m.sum(assignments[i], "<=", 1).post();
    }

    // each car is assigned to at most one participant
    for (int j = 0; j < nCars; j++) {
      BoolVar[] column = new BoolVar[nParticipants];
      for (int i = 0; i < nParticipants; i++) column[i] = assignments[i][j];
      m.sum(column, "<=", 1).post();
    }

    // maximise the total number of assignments
    BoolVar[] all = new BoolVar[nParticipants * nCars];
    for (int i = 0; i < nParticipants; i++)
      for (int j = 0; j < nCars; j++) all[i * nCars + j] = assignments[i][j];
    IntVar total = m.sum("total", all);
    m.setObjective(Model.MAXIMIZE, total);

    out.put("assignments", assignments);
  }
}
