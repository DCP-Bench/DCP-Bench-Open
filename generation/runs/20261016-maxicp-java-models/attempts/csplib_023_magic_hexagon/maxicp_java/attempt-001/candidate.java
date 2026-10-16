import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Magic hexagon: the numbers 1..NUM_CELLS are placed once each on the 19 cells A..S of a hexagon,
// so that each of the 15 lines (5 rows, 5 lines in one diagonal direction, 5 in the other)
// sums to MAGIC_SUM. Cells are indexed A=0, B=1, ..., S=18, in the order of the output LD.
//
//       A, B, C
//      D, E, F, G
//     H, I, J, K, L
//      M, N, O, P
//       Q, R, S
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numCells = inst.getInt("NUM_CELLS");
    int magic = inst.getInt("MAGIC_SUM");
    if (numCells != 19) {
      throw new IllegalArgumentException("the hexagon has 19 cells, got NUM_CELLS = " + numCells);
    }

    // the cells hold the numbers 1 to NUM_CELLS
    CPIntVar[] v = m.intVarArray(19, 1, numCells);

    // all cells hold different numbers
    m.cp().post(allDifferent(v));

    // the three rows of the top half and the two rows of the bottom half each add up to the magic sum
    // top row A B C
    m.cp().post(sum(sub(v, 0, 1, 2), magic));
    // second row D E F G
    m.cp().post(sum(sub(v, 3, 4, 5, 6), magic));
    // middle row H I J K L
    m.cp().post(sum(sub(v, 7, 8, 9, 10, 11), magic));
    // fourth row M N O P
    m.cp().post(sum(sub(v, 12, 13, 14, 15), magic));
    // bottom row Q R S
    m.cp().post(sum(sub(v, 16, 17, 18), magic));

    // the diagonal from the upper left down to the lower left: A D H, B E I M, C F J N Q
    // (and the lines on the far side: G K O R, L P S), each adds up to the magic sum
    m.cp().post(sum(sub(v, 0, 3, 7), magic));
    m.cp().post(sum(sub(v, 1, 4, 8, 12), magic));
    m.cp().post(sum(sub(v, 2, 5, 9, 13, 16), magic));
    m.cp().post(sum(sub(v, 6, 10, 14, 17), magic));
    m.cp().post(sum(sub(v, 11, 15, 18), magic));

    // the diagonal from the upper right down to the lower right: C G L, B F K P, A E J O S
    // (and the lines on the far side: D I N R, H M Q), each adds up to the magic sum
    m.cp().post(sum(sub(v, 7, 12, 16), magic));
    m.cp().post(sum(sub(v, 3, 8, 13, 17), magic));
    m.cp().post(sum(sub(v, 0, 4, 9, 14, 18), magic));
    m.cp().post(sum(sub(v, 1, 5, 10, 15), magic));
    m.cp().post(sum(sub(v, 2, 6, 11), magic));

    out.put("LD", v);
  }

  // the variables at the given positions of v, in that order
  private static CPIntVar[] sub(CPIntVar[] v, int... idx) {
    CPIntVar[] r = new CPIntVar[idx.length];
    for (int i = 0; i < idx.length; i++) r[i] = v[idx[i]];
    return r;
  }
}
