import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Huey, Dewey and Louie are questioned by their uncle; decide who (if any) is guilty
// from their three statements, given that the cub scouts cannot tell a lie.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    BoolVar huey = m.boolVar("huey");
    BoolVar dewey = m.boolVar("dewey");
    BoolVar louie = m.boolVar("louie");

    // Huey: Dewey and Louie have equal share in it; if one is guilty, so is the other
    m.arithm(dewey, "=", louie).post();

    // Dewey: if Huey is guilty, then so am I
    m.arithm(huey, "<=", dewey).post();

    // Louie: Dewey and I are not both guilty
    m.arithm(dewey, "+", louie, "<=", 1).post();

    out.put("dewey", dewey);
    out.put("huey", huey);
    out.put("louie", louie);
  }
}
