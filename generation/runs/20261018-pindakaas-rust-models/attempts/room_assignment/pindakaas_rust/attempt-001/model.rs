// Room assignment: assign each request to one of max_rooms rooms (0-based), so that
// each request is in one room for its entire duration, and no two overlapping
// requests share a room. Some requests have a pre-assigned room (value >= 0; -1 means none).
// Dates are ISO strings (YYYY-MM-DD), so lexicographic order is date order.
// A request runs from its start date up to, but not including, its end date.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.len("start_data");
    let starts = inst.strings("start_data");
    let ends = inst.strings("end_data");
    let pre = inst.ints("preassigned_room_data");
    let max_rooms = inst.int("max_rooms");

    // Room of each request, 0..max_rooms-1.
    let rooms: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=max_rooms - 1)).collect();

    // Some requests have a pre-assigned room: that request stays in it.
    for i in 0..n {
        if pre[i] >= 0 {
            post(s, iv(&rooms[i]), Comparator::Equal, pre[i])?;
        }
    }

    // A room can only serve one request at a time: overlapping requests use different rooms.
    // Requests i and j overlap when start_i < end_j and start_j < end_i.
    // Back-to-back requests (end_i == start_j) do not overlap.
    for i in 0..n {
        for j in (i + 1)..n {
            if starts[i] < ends[j] && starts[j] < ends[i] {
                all_different(s, &[rooms[i].clone(), rooms[j].clone()])?;
            }
        }
    }

    let mut out = Out::new();
    out.put("room_assignments", &rooms);
    Ok(out)
}
