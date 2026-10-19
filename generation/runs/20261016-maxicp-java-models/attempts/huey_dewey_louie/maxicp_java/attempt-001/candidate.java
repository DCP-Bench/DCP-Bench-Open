// Huey, Dewey and Louie are questioned by their uncle. Each of them is guilty or not.
// They are cub scouts and cannot tell a lie, so each of their three statements is true.
// Decide who (if any) of Huey, Dewey and Louie is guilty.
import org.maxicp.cp.engine.core.CPBoolVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    CPBoolVar huey = m.boolVar();   // huey = 1 if Huey is guilty
    CPBoolVar dewey = m.boolVar();  // dewey = 1 if Dewey is guilty
    CPBoolVar louie = m.boolVar();  // louie = 1 if Louie is guilty

    // Huey: Dewey and Louie have equal share in it; if one is guilty, so is the other.
    m.cp().post(eq(dewey, louie));

    // Dewey: If Huey is guilty, then so am I.
    m.cp().post(implies(huey, dewey));

    // Louie: Dewey and I are not both guilty.
    m.cp().post(le(sum(dewey, louie), 1));

    out.put("huey", huey);
    out.put("dewey", dewey);
    out.put("louie", louie);
  }
}
