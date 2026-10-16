import com.google.gson.JsonArray;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Movie scheduling: accept the largest set of movie offers such that no two accepted
// movies have filming periods that overlap. Each offer is [title, first day, last day].
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // Each movie is a row [title, first day, last day]; the title is a string.
    JsonArray movies = inst.raw("movies").getAsJsonArray();
    int n = movies.size();
    int[] first = new int[n];
    int[] last = new int[n];
    for (int i = 0; i < n; i++) {
      JsonArray row = movies.get(i).getAsJsonArray();
      first[i] = row.get(1).getAsInt();
      last[i] = row.get(2).getAsInt();
    }

    // Print which movies are accepted, as a list of booleans in the input order.
    CPBoolVar[] selected = m.boolVarArray(n);

    // Each movie is accepted or not; a film whose days overlap another cannot be taken with it.
    // Filming periods are closed intervals of days, so periods that share a day overlap.
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (first[i] <= last[j] && first[j] <= last[i]) {
          // you cannot simultaneously accept two jobs whose intervals overlap
          m.cp().post(or(new CPBoolVar[] {not(selected[i]), not(selected[j])}));
        }
      }
    }

    // you seek the largest possible set of jobs
    CPIntVar count = m.intVar(0, n);
    m.cp().post(eq(sum(selected), count));
    m.maximize(count);

    out.put("selected_movies", selected);
  }
}
