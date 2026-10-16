// Movie scheduling (maximum set of non-overlapping intervals): choose the largest set of
// movie offers so that no two chosen films overlap. Each film is an inclusive interval of
// filming days [first day, last day]. The film titles are the first entry of each row.
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // each movie is [title, first day, last day]; the title is mixed with the ints, so read raw
    JsonArray movies = inst.raw("movies").getAsJsonArray();
    int n = movies.size();
    int[] first = new int[n];
    int[] last = new int[n];
    for (int i = 0; i < n; i++) {
      JsonArray row = movies.get(i).getAsJsonArray();
      first[i] = row.get(1).getAsInt();
      last[i] = row.get(2).getAsInt();
    }

    // selected[i] = 1 if movie i is accepted
    BoolVar[] selected = m.boolVarArray("selected", n);

    // you cannot accept two jobs whose intervals overlap: on every day that a film starts,
    // at most one of the films running that day is accepted (the intervals overlap exactly
    // when they share such a day, so these day constraints cover every overlap)
    for (int d = 0; d < n; d++) {
      int day = first[d];
      int covering = 0;
      for (int i = 0; i < n; i++) {
        if (first[i] <= day && day <= last[i]) covering++;
      }
      if (covering < 2) continue;
      BoolVar[] running = new BoolVar[covering];
      int k = 0;
      for (int i = 0; i < n; i++) {
        if (first[i] <= day && day <= last[i]) running[k++] = selected[i];
      }
      m.sum(running, "<=", 1).post();
    }

    // you want the largest possible set of jobs: maximise the number of accepted films
    IntVar count = m.sum("count", selected);
    m.setObjective(Model.MAXIMIZE, count);

    out.put("selected_movies", selected);
  }
}
