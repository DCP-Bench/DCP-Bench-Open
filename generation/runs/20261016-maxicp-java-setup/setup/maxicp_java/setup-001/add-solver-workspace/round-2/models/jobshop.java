import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Schedule the tasks of every job in order, one task at a time per machine, minimising the makespan.
public class JobShop {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        JsonArray jobs = data.getAsJsonArray("jobs");
        int nJobs = jobs.size();
        int nMachines = 0;
        for (int j = 0; j < nJobs; j++)
            for (var task : jobs.get(j).getAsJsonArray())
                nMachines = Math.max(nMachines, task.getAsJsonArray().get(0).getAsInt() + 1);

        CPSolver cp = CPFactory.makeSolver();
        // one interval per task, and every task must run
        CPIntervalVar[][] task = new CPIntervalVar[nJobs][];
        List<CPIntervalVar> all = new ArrayList<>();
        for (int j = 0; j < nJobs; j++) {
            JsonArray row = jobs.get(j).getAsJsonArray();
            task[j] = new CPIntervalVar[row.size()];
            for (int k = 0; k < row.size(); k++) {
                int duration = row.get(k).getAsJsonArray().get(1).getAsInt();
                task[j][k] = makeIntervalVar(cp, false, duration);
                all.add(task[j][k]);
            }
        }

        // the tasks of a job run in the given order
        for (int j = 0; j < nJobs; j++)
            for (int k = 0; k + 1 < task[j].length; k++)
                cp.post(endBeforeStart(task[j][k], task[j][k + 1]));

        // a machine runs at most one task at a time
        for (int m = 0; m < nMachines; m++) {
            List<CPIntervalVar> onMachine = new ArrayList<>();
            for (int j = 0; j < nJobs; j++) {
                JsonArray row = jobs.get(j).getAsJsonArray();
                for (int k = 0; k < row.size(); k++)
                    if (row.get(k).getAsJsonArray().get(0).getAsInt() == m) onMachine.add(task[j][k]);
            }
            cp.post(noOverlap(onMachine.toArray(new CPIntervalVar[0])));
        }

        // the makespan is the end of the last task
        CPIntVar makespan = makespan(all.toArray(new CPIntervalVar[0]));

        // branch on start times
        List<CPIntVar> starts = new ArrayList<>();
        for (CPIntervalVar t : all) starts.add(start(t));
        CPIntVar[] startArray = starts.toArray(new CPIntVar[0]);

        int[][] best = new int[nJobs][];
        for (int j = 0; j < nJobs; j++) best[j] = new int[task[j].length];
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(startArray));
        search.onSolution(() -> {
            int idx = 0;
            for (int j = 0; j < nJobs; j++)
                for (int k = 0; k < task[j].length; k++) best[j][k] = startArray[idx++].min();
        });
        SearchStatistics stats = search.optimize(cp.minimize(makespan));
        if (!stats.isCompleted()) {
            System.out.println("Optimum not proven");
            return;
        }
        System.out.println("{\"start\": " + Arrays.deepToString(best) + "}");
    }
}
