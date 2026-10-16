// Pack rectangular items, without rotation, into the smallest rectangle that holds them all
// with no overlap. Output pos_x, pos_y: the lower-left corner of each item, counted from 0.
// total_x, total_y: the width and height of the enclosing rectangle. Minimise its area.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
    public static void build(Instance inst, Model m, Outputs out) {
        // the items: widths[i] and heights[i] are the size of item i (the instance gives them)
        int[] widths = inst.getIntArray("widths");
        int[] heights = inst.getIntArray("heights");
        int n = widths.length;

        int sumW = 0, sumH = 0, maxW = 0, maxH = 0;
        for (int i = 0; i < n; i++) {
            sumW += widths[i];
            sumH += heights[i];
            maxW = Math.max(maxW, widths[i]);
            maxH = Math.max(maxH, heights[i]);
        }

        // the items fill at least their total area: totalX * totalY >= sumArea
        // (a derived bound, not stated in the problem). The enclosing rectangle is at least as
        // wide as the widest item and at most as wide as all items side by side; the same for its height
        int sumArea = 0;
        for (int i = 0; i < n; i++) sumArea += widths[i] * heights[i];
        CPIntVar totalX = m.intVar(Math.max(maxW, ceilDiv(sumArea, sumH)), sumW);
        CPIntVar totalY = m.intVar(Math.max(maxH, ceilDiv(sumArea, sumW)), sumH);

        // the position of each item: its left edge and its bottom edge, counted from 0
        CPIntVar[] posX = new CPIntVar[n];
        CPIntVar[] posY = new CPIntVar[n];
        for (int i = 0; i < n; i++) {
            posX[i] = m.intVar(0, sumW - widths[i]);
            posY[i] = m.intVar(0, sumH - heights[i]);
        }

        // every item lies within the boundaries of the enclosing rectangle
        for (int i = 0; i < n; i++) {
            m.cp().post(ge(totalX, plus(posX[i], widths[i])));
            m.cp().post(ge(totalY, plus(posY[i], heights[i])));
        }

        // no two items overlap: for each pair, one lies to the left of the other, or
        // one lies below the other
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                CPBoolVar iLeftOfJ = isLe(plus(posX[i], widths[i]), posX[j]);
                CPBoolVar jLeftOfI = isLe(plus(posX[j], widths[j]), posX[i]);
                CPBoolVar iBelowJ = isLe(plus(posY[i], heights[i]), posY[j]);
                CPBoolVar jBelowI = isLe(plus(posY[j], heights[j]), posY[i]);
                m.cp().post(or(new CPBoolVar[] {iLeftOfJ, jLeftOfI, iBelowJ, jBelowI}));
            }
        }

        // the objective is the area of the enclosing rectangle, to be minimised
        CPIntVar area = m.intVar(sumArea, sumW * sumH);
        m.cp().post(eq(area, mul(totalX, totalY)));
        m.minimize(area);

        out.put("pos_x", posX);
        out.put("pos_y", posY);
        out.put("total_x", totalX);
        out.put("total_y", totalY);
    }

    private static int ceilDiv(int a, int b) {
        return (a + b - 1) / b;
    }
}
