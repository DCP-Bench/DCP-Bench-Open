import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Schedule the tasks of each job in order, one task at a time per machine, minimising the makespan.
public class JobShop {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        JsonArray jobs = data.getAsJsonArray("jobs");
        int nJobs = jobs.size();
        int[][] machine = new int[nJobs][];
        int[][] duration = new int[nJobs][];
        int maxMachine = 0;
        for (int j = 0; j < nJobs; j++) {
            JsonArray tasks = jobs.get(j).getAsJsonArray();
            machine[j] = new int[tasks.size()];
            duration[j] = new int[tasks.size()];
            for (int k = 0; k < tasks.size(); k++) {
                JsonArray t = tasks.get(k).getAsJsonArray();
                machine[j][k] = t.get(0).getAsInt();
                duration[j][k] = t.get(1).getAsInt();
                maxMachine = Math.max(maxMachine, machine[j][k]);
            }
        }

        CPSolver cp = makeSolver();
        try {
            // task[j][k]: task k of job j, which must run
            CPIntervalVar[][] task = new CPIntervalVar[nJobs][];
            List<CPIntervalVar> all = new ArrayList<>();
            for (int j = 0; j < nJobs; j++) {
                task[j] = new CPIntervalVar[duration[j].length];
                for (int k = 0; k < duration[j].length; k++) {
                    task[j][k] = makeIntervalVar(cp, false, duration[j][k]);
                    all.add(task[j][k]);
                }
            }
            // the tasks of a job run in the given order
            for (int j = 0; j < nJobs; j++) {
                for (int k = 0; k + 1 < duration[j].length; k++) {
                    cp.post(endBeforeStart(task[j][k], task[j][k + 1]));
                }
            }
            // a machine runs at most one task at a time
            for (int m = 0; m <= maxMachine; m++) {
                List<CPIntervalVar> onMachine = new ArrayList<>();
                for (int j = 0; j < nJobs; j++)
                    for (int k = 0; k < duration[j].length; k++)
                        if (machine[j][k] == m) onMachine.add(task[j][k]);
                if (!onMachine.isEmpty()) cp.post(noOverlap(onMachine.toArray(new CPIntervalVar[0])));
            }

            // the makespan is the end of the last task
            CPIntVar makespan = makespan(all.toArray(new CPIntervalVar[0]));

            // branch on the start times
            List<CPIntVar> starts = new ArrayList<>();
            for (CPIntervalVar t : all) starts.add(start(t));
            CPIntVar[] startArr = starts.toArray(new CPIntVar[0]);

            int[][] when = new int[nJobs][];
            for (int j = 0; j < nJobs; j++) when[j] = new int[duration[j].length];
            DFSearch search = makeDfs(cp, firstFailBinary(startArr));
            search.onSolution(() -> {
                int idx = 0;
                for (int j = 0; j < nJobs; j++)
                    for (int k = 0; k < duration[j].length; k++)
                        when[j][k] = startArr[idx++].min();
            });
            SearchStatistics stats = search.optimize(cp.minimize(makespan));
            if (stats.numberOfSolutions() == 0) {
                System.out.println("{\"status\": \"unsatisfiable\"}");
            } else if (!stats.isCompleted()) {
                System.out.println("Optimum not proven");
            } else {
                StringBuilder out = new StringBuilder("{\"start\": [");
                for (int j = 0; j < nJobs; j++) {
                    if (j > 0) out.append(", ");
                    out.append(Arrays.toString(when[j]));
                }
                out.append("]}");
                System.out.println(out);
            }
        } catch (InconsistencyException e) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
        }
    }
}
