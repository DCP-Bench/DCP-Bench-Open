import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Four people (0-3) hold eight different jobs, two each. Find which person holds each job.
public class Submission {

  // the jobs, in the order of the outputs
  static final String[] JOBS = {"chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"};
  static final int PEOPLE = 4;

  static int job(String name) {
    return java.util.Arrays.asList(JOBS).indexOf(name);
  }

  public static void build(Instance inst, Model m, Outputs out) {
    int nJobs = JOBS.length;

    // x[p][j] = 1 if person p holds job j
    BoolVar[][] x = new BoolVar[PEOPLE][nJobs];
    for (int p = 0; p < PEOPLE; p++)
      for (int j = 0; j < nJobs; j++) x[p][j] = m.boolVar("x" + p + "_" + JOBS[j]);

    // each job is held by exactly one person
    for (int j = 0; j < nJobs; j++) {
      BoolVar[] holders = new BoolVar[PEOPLE];
      for (int p = 0; p < PEOPLE; p++) holders[p] = x[p][j];
      m.sum(holders, "=", 1).post();
    }

    // each person holds exactly two jobs
    for (int p = 0; p < PEOPLE; p++) m.sum(x[p], "=", 2).post();

    // clue 1: the nurse is not a teacher, police officer, or clerk
    for (String other : new String[]{"teacher", "police_officer", "clerk"}) {
      for (int p = 0; p < PEOPLE; p++)
        m.arithm(x[p][job("nurse")], "+", x[p][job(other)], "<=", 1).post();
    }

    // clue 2: the clerk is not the chef
    for (int p = 0; p < PEOPLE; p++)
      m.arithm(x[p][job("clerk")], "+", x[p][job("chef")], "<=", 1).post();

    // clue 3: person 0 is not the boxer
    m.arithm(x[0][job("boxer")], "=", 0).post();

    // clue 4: person 3 is not the teacher, police officer, or nurse
    for (String other : new String[]{"teacher", "police_officer", "nurse"})
      m.arithm(x[3][job(other)], "=", 0).post();

    // clue 5: person 0, the chef, and the police officer went golfing together,
    // so they are three different people: person 0 is neither the chef nor the police officer,
    // and the chef and the police officer are different people
    m.arithm(x[0][job("chef")], "=", 0).post();
    m.arithm(x[0][job("police_officer")], "=", 0).post();
    for (int p = 0; p < PEOPLE; p++)
      m.arithm(x[p][job("chef")], "+", x[p][job("police_officer")], "<=", 1).post();

    // the person index holding each job
    for (int j = 0; j < nJobs; j++) {
      IntVar person = m.intVar(JOBS[j], 0, PEOPLE - 1);
      int[] index = new int[PEOPLE];
      for (int p = 0; p < PEOPLE; p++) index[p] = p;
      BoolVar[] holders = new BoolVar[PEOPLE];
      for (int p = 0; p < PEOPLE; p++) holders[p] = x[p][j];
      m.scalar(holders, index, "=", person).post();
      out.put(JOBS[j], person);
    }
  }
}
