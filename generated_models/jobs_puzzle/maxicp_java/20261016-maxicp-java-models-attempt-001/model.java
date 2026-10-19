import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Four people hold eight different jobs; each person holds exactly two jobs.
// Each job is assigned to exactly one person, with the person index 0-3 as the value.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // jobs: chef, guard, nurse, clerk, police officer, teacher, actor, boxer
    CPIntVar chef = m.intVar(0, 3);
    CPIntVar guard = m.intVar(0, 3);
    CPIntVar nurse = m.intVar(0, 3);
    CPIntVar clerk = m.intVar(0, 3);
    CPIntVar police = m.intVar(0, 3);
    CPIntVar teacher = m.intVar(0, 3);
    CPIntVar actor = m.intVar(0, 3);
    CPIntVar boxer = m.intVar(0, 3);
    CPIntVar[] jobs = {chef, guard, nurse, clerk, police, teacher, actor, boxer};

    // Each person holds exactly two jobs.
    for (int p = 0; p < 4; p++) {
      CPIntVar[] holds = new CPIntVar[jobs.length];
      for (int j = 0; j < jobs.length; j++) {
        holds[j] = isEq(jobs[j], p);
      }
      m.cp().post(eq(sum(holds), 2));
    }

    // The nurse is not a teacher, police officer, or clerk.
    m.cp().post(neq(nurse, teacher));
    m.cp().post(neq(nurse, police));
    m.cp().post(neq(nurse, clerk));

    // The clerk is not the chef.
    m.cp().post(neq(clerk, chef));

    // Person 0 is not the boxer.
    m.cp().post(neq(boxer, 0));

    // Person 3 is not the teacher, police officer, or nurse.
    m.cp().post(neq(teacher, 3));
    m.cp().post(neq(police, 3));
    m.cp().post(neq(nurse, 3));

    // Person 0, the chef, and the police officer went golfing together.
    m.cp().post(neq(chef, 0));
    m.cp().post(neq(police, 0));
    m.cp().post(neq(chef, police));

    out.put("actor", actor);
    out.put("boxer", boxer);
    out.put("chef", chef);
    out.put("clerk", clerk);
    out.put("guard", guard);
    out.put("nurse", nurse);
    out.put("police_officer", police);
    out.put("teacher", teacher);
  }
}
