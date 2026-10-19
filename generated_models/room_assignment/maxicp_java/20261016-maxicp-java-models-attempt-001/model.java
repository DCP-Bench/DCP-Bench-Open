// Room assignment: each request is given one room, for its whole stay, among max_rooms rooms.
// A room serves one request at a time: no two overlapping requests share a room.
// Some requests are already pre-assigned to a room (-1 means not pre-assigned).
// A stay runs from its start date up to, not including, its end date.

import java.time.LocalDate;

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int maxRooms = inst.getInt("max_rooms");
    String[] startData = inst.getStringArray("start_data");
    String[] endData = inst.getStringArray("end_data");
    int[] preassigned = inst.getIntArray("preassigned_room_data");
    int n = startData.length;

    long[] start = new long[n];
    long[] end = new long[n];
    for (int i = 0; i < n; i++) {
      start[i] = LocalDate.parse(startData[i]).toEpochDay();
      end[i] = LocalDate.parse(endData[i]).toEpochDay();
    }

    // every request is assigned one room out of max_rooms rooms
    CPIntVar[] room = m.intVarArray(n, 0, maxRooms - 1);

    // some requests are already assigned a room, and keep it
    for (int i = 0; i < n; i++) {
      if (preassigned[i] >= 0) {
        m.cp().post(eq(room[i], preassigned[i]));
      }
    }

    // a room can only serve one request at a time: two requests whose stays overlap
    // cannot be assigned the same room
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (start[i] < end[j] && start[j] < end[i]) {
          m.cp().post(neq(room[i], room[j]));
        }
      }
    }

    out.put("room_assignments", room);
  }
}
