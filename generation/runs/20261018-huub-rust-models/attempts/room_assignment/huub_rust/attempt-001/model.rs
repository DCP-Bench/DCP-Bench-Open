// Room assignment: assign each request to one of max_rooms rooms (0-based) so that
// each request keeps its room for its whole stay, and no two overlapping requests
// share a room. Some requests are pre-assigned to a room. Dates are YYYY-MM-DD strings;
// a stay runs from its start date up to, not including, its end date.

// Days since 1970-01-01 for a YYYY-MM-DD date (proleptic Gregorian calendar).
fn days(s: &str) -> i64 {
    let p: Vec<i64> = s.split('-').map(|t| t.parse().unwrap()).collect();
    let (y, m, d) = (p[0], p[1], p[2]);
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146097 + doe - 719468
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let max_rooms = inst.int("max_rooms");
    let starts: Vec<i64> = inst.strings("start_data").iter().map(|s| days(s)).collect();
    let ends: Vec<i64> = inst.strings("end_data").iter().map(|s| days(s)).collect();
    let pre = inst.ints("preassigned_room_data");
    let n = starts.len();

    // Room of each request: a fixed room when pre-assigned, otherwise any room.
    let mut rooms = Vec::with_capacity(n);
    for i in 0..n {
        let r = if pre[i] >= 0 {
            m.new_int_decision(pre[i]..=pre[i])
        } else {
            m.new_int_decision(0..=max_rooms - 1)
        };
        rooms.push(r);
    }

    // A room can serve only one request at a time: overlapping requests use different rooms.
    // Two stays overlap when each starts before the other ends.
    for i in 0..n {
        for j in i + 1..n {
            if starts[i] < ends[j] && starts[j] < ends[i] {
                m.linear(rooms[i] - rooms[j]).ne(0).post()?;
            }
        }
    }

    let mut out = Out::new();
    out.put("room_assignments", rooms);
    Ok(out)
}
