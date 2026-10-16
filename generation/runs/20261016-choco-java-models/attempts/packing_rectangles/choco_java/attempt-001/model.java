// Rectangular packing: place rectangular items (widths, heights from the instance)
// inside a container of size total_x by total_y so that no two items overlap and every
// item lies within the container, minimising the container's total area.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] widths = inst.getIntArray("widths");   // width of each item
    int[] heights = inst.getIntArray("heights"); // height of each item
    int n = widths.length;

    // every item placed side by side in a row is a valid container, so these bound the container
    int sumW = 0, sumH = 0;
    for (int i = 0; i < n; i++) { sumW += widths[i]; sumH += heights[i]; }

    IntVar totalX = m.intVar("total_x", 1, sumW);  // width of the larger rectangle
    IntVar totalY = m.intVar("total_y", 1, sumH);  // height of the larger rectangle

    // lower-left corner of each item, counted from 0
    IntVar[] posX = new IntVar[n];
    IntVar[] posY = new IntVar[n];
    IntVar[] w = new IntVar[n];
    IntVar[] h = new IntVar[n];
    for (int i = 0; i < n; i++) {
      posX[i] = m.intVar("pos_x_" + i, 0, sumW);
      posY[i] = m.intVar("pos_y_" + i, 0, sumH);
      w[i] = m.intVar(widths[i]);
      h[i] = m.intVar(heights[i]);
    }

    // no two items overlap
    m.diffN(posX, posY, w, h, true).post();

    // every item lies within the boundaries of the larger rectangle
    for (int i = 0; i < n; i++) {
      posX[i].add(widths[i]).le(totalX).post();
      posY[i].add(heights[i]).le(totalY).post();
    }

    // the objective is the total area of the larger rectangle
    IntVar area = m.intVar("area", 1, sumW * sumH, true);
    m.times(totalX, totalY, area).post();
    m.setObjective(Model.MINIMIZE, area);

    out.put("pos_x", posX);
    out.put("pos_y", posY);
    out.put("total_x", totalX);
    out.put("total_y", totalY);
  }
}
