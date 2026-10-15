# DCP-Bench examples for choco_java

Two complete submissions for invented problems, each run through the choco_java
driver in the image on the instance shown. They show globals working together. The roster
uses a matrix with global cardinality, an automaton over each row and table costs through
`element`. The machine schedule uses optional tasks on per-machine cumulatives, a crew
cumulative, value precedence, and dom/wdeg with Luby restarts.

## Shift roster: matrix, globalCardinality, regular, element, minimise

Instance: `{"workers": 4, "days": 7, "demand": [[1,1],[1,1],[2,1],[1,1],[1,1],[1,0],[0,1]], "cost": [[3,5],[4,4],[2,6],[5,3]]}`.
Proven optimum 34 in 0.5 s; it is the only optimal roster.

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.nary.automata.FA.FiniteAutomaton;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Shift roster: give every worker a shift (0 off, 1 day, 2 night) on every day so
// that each day's demand is met, no one works a day shift right after a night,
// nights come in runs of at most two, and the total cost of the roster is minimal.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int workers = inst.getInt("workers"), days = inst.getInt("days");
    int[][] demand = inst.getIntMatrix("demand");  // per day: [day shifts, night shifts]
    int[][] cost = inst.getIntMatrix("cost");      // per worker: [day cost, night cost]
    IntVar[][] shift = m.intVarMatrix("shift", workers, days, 0, 2);

    // each day needs exactly demand[d] day and night shifts; the rest are off
    for (int d = 0; d < days; d++) {
      IntVar[] column = new IntVar[workers];
      for (int w = 0; w < workers; w++) column[w] = shift[w][d];
      IntVar[] occurrences = {
          m.intVar(workers - demand[d][0] - demand[d][1]), m.intVar(demand[d][0]), m.intVar(demand[d][1])};
      m.globalCardinality(column, new int[]{0, 1, 2}, occurrences, true).post();
    }

    // no day shift right after a night, and at most two nights in a row
    FiniteAutomaton rules = new FiniteAutomaton("(0|1|20|220)*(2|22)?");
    for (int w = 0; w < workers; w++) m.regular(shift[w], rules).post();

    // minimise the total cost: a day shift costs cost[w][0], a night cost[w][1]
    IntVar[] paid = new IntVar[workers * days];
    for (int w = 0; w < workers; w++)
      for (int d = 0; d < days; d++)
        paid[w * days + d] = m.element("paid", new int[]{0, cost[w][0], cost[w][1]}, shift[w][d]);
    IntVar total = m.intVar("total", 0, workers * days * 100, true);
    m.sum(paid, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    // fill the cheapest choices first
    m.getSolver().setSearch(Search.minDomLBSearch(paid));

    out.put("shift", shift);
    out.put("total", total);
  }
}
```

## Parallel machines with a shared crew: optional tasks, cumulative, precedence, restarts

Instance: `{"machines": 2, "crew_size": 3, "duration": [3, 2, 4, 2, 3, 1], "release": [0, 0, 1, 2, 3, 0], "crew": [2, 1, 1, 2, 1, 2]}`.
Proven optimum 8 in 0.1 s. The total work of 15 on two machines gives the bound 7.5.

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.Task;
import dcp.Instance;
import dcp.Outputs;

// Parallel machines with a shared crew: every task runs once, without interruption,
// on one of the identical machines, not before its release time; a machine runs one
// task at a time; the tasks running at any moment need at most crew_size workers.
// Minimise the time the last task ends.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int machines = inst.getInt("machines"), crewSize = inst.getInt("crew_size");
    int[] duration = inst.getIntArray("duration"), release = inst.getIntArray("release");
    int[] crew = inst.getIntArray("crew");
    int n = duration.length;
    int horizon = 0;
    for (int i = 0; i < n; i++) horizon = Math.max(horizon, release[i]) + duration[i];

    IntVar[] start = new IntVar[n];
    IntVar[] end = new IntVar[n];
    Task[] tasks = new Task[n];
    for (int i = 0; i < n; i++) {
      // not before its release time
      start[i] = m.intVar("start" + i, release[i], horizon - duration[i], true);
      end[i] = m.offset(start[i], duration[i]);
      tasks[i] = new Task(start[i], duration[i]);
    }
    IntVar[] machine = m.intVarArray("machine", n, 0, machines - 1);

    // a machine runs one task at a time: an optional copy of each task per machine
    for (int k = 0; k < machines; k++) {
      Task[] onK = new Task[n];
      IntVar[] one = new IntVar[n];
      for (int i = 0; i < n; i++) {
        BoolVar here = m.isEq(machine[i], k);
        onK[i] = m.taskVar(start[i], duration[i], here);
        one[i] = m.intVar(1);
      }
      m.cumulative(onK, one, m.intVar(1)).post();
    }

    // the tasks running at any moment need at most crew_size workers
    IntVar[] need = new IntVar[n];
    for (int i = 0; i < n; i++) need[i] = m.intVar(crew[i]);
    m.cumulative(tasks, need, m.intVar(crewSize)).post();

    // the machines are identical: machine k+1 is used only after machine k
    int[] order = new int[machines];
    for (int k = 0; k < machines; k++) order[k] = k;
    m.intValuePrecedeChain(machine, order).post();

    // minimise the time the last task ends
    IntVar makespan = m.intVar("makespan", 0, horizon, true);
    m.max(makespan, end).post();
    m.setObjective(Model.MINIMIZE, makespan);

    m.getSolver().setSearch(Search.domOverWDegSearch(machine), Search.inputOrderLBSearch(start));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("start", start);
    out.put("machine", machine);
    out.put("makespan", makespan);
  }
}
```
