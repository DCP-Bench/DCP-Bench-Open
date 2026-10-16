// Room assignment: give each request one room (0 to max_rooms - 1) for its whole stay,
// so that no two requests whose stays overlap share a room. Some requests are
// pre-assigned to a room. A stay runs from its start date up to, not including, its end date.
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int maxRooms = inst.getInt("max_rooms");                  // number of rooms
    String[] startData = inst.getStringArray("start_data");   // check-in dates, YYYY-MM-DD
    String[] endData = inst.getStringArray("end_data");       // check-out dates, exclusive
    int[] preassigned = inst.getIntArray("preassigned_room_data"); // room, or -1 for none
    int n = startData.length;

    // stay of request i as day numbers
    long[] start = new long[n];
    long[] end = new long[n];
    for (int i = 0; i < n; i++) {
      start[i] = LocalDate.parse(startData[i]).toEpochDay();
      end[i] = LocalDate.parse(endData[i]).toEpochDay();
    }

    // room of each request
    IntVar[] room = m.intVarArray("room", n, 0, maxRooms - 1);

    // a pre-assigned request keeps its room
    for (int i = 0; i < n; i++) {
      if (preassigned[i] >= 0) m.arithm(room[i], "=", preassigned[i]).post();
    }

    // requests present on the same day need different rooms: for the day each stay starts,
    // all stays covering that day must be in different rooms (this covers every overlap,
    // since two overlapping stays both cover the later start day)
    for (int d = 0; d < n; d++) {
      List<IntVar> present = new ArrayList<>();
      for (int i = 0; i < n; i++) {
        if (start[i] <= start[d] && start[d] < end[i]) present.add(room[i]);
      }
      if (present.size() >= 2) {
        m.allDifferent(present.toArray(new IntVar[0]), "AC").post();
      }
    }

    out.put("room_assignments", room);
  }
}
