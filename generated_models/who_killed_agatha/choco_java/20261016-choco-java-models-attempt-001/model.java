// Who killed Aunt Agatha in Dreadsbury Mansion: Agatha, the butler and Charles.
// Persons are indexed 0 = Agatha, 1 = the butler, 2 = Charles.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getStringArray("names").length;   // persons living in the mansion
    final int AGATHA = 0, BUTLER = 1, CHARLES = 2;

    // hates[x][y] = 1 if person x hates person y; richer[x][y] = 1 if x is richer than y
    BoolVar[][] hates = new BoolVar[n][n];
    BoolVar[][] richer = new BoolVar[n][n];
    for (int x = 0; x < n; x++) {
      for (int y = 0; y < n; y++) {
        hates[x][y] = m.boolVar("hates_" + x + "_" + y);
        richer[x][y] = m.boolVar("richer_" + x + "_" + y);
      }
    }

    // nobody is richer than himself
    for (int x = 0; x < n; x++) m.arithm(richer[x][x], "=", 0).post();

    // the killer is one of the three persons
    IntVar killer = m.intVar("killer", 0, n - 1);

    // a killer always hates his victim (Agatha) and is no richer than her
    IntVar[] hatesAgatha = new IntVar[n];
    IntVar[] richerThanAgatha = new IntVar[n];
    for (int x = 0; x < n; x++) {
      hatesAgatha[x] = hates[x][AGATHA];
      richerThanAgatha[x] = richer[x][AGATHA];
    }
    m.element(m.intVar(1), hatesAgatha, killer, 0).post();
    m.element(m.intVar(0), richerThanAgatha, killer, 0).post();

    // Charles hates noone that Agatha hates
    for (int x = 0; x < n; x++) m.arithm(hates[AGATHA][x], "+", hates[CHARLES][x], "<=", 1).post();

    // Agatha hates everybody except the butler
    for (int x = 0; x < n; x++) m.arithm(hates[AGATHA][x], "=", x == BUTLER ? 0 : 1).post();

    // the butler hates everyone not richer than Aunt Agatha
    for (int x = 0; x < n; x++) m.sum(new IntVar[]{richer[x][AGATHA], hates[BUTLER][x]}, ">=", 1).post();

    // the butler hates everyone whom Agatha hates
    for (int x = 0; x < n; x++) m.arithm(hates[AGATHA][x], "<=", hates[BUTLER][x]).post();

    // noone hates everyone: each person hates at most n-1 people
    for (int x = 0; x < n; x++) m.sum(hates[x], "<=", n - 1).post();

    out.put("killer", killer);
  }
}
