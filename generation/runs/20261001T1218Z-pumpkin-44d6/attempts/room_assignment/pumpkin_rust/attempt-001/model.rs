// Room assignment: give every request one room for its whole stay, keeping the
// rooms some requests already have, so that no room serves two requests on the
// same day.

// Day number of a "YYYY-MM-DD" date (days since 1970-01-01, proleptic Gregorian
// calendar), so that dates can be compared and subtracted as integers.
fn day_number(date: &str) -> i64 {
    let parts: Vec<i64> = date
        .split('-')
        .map(|p| p.parse::<i64>().expect("date: expected YYYY-MM-DD"))
        .collect();
    let (mut y, m, d) = (parts[0], parts[1], parts[2]);
    if m <= 2 {
        y -= 1;
    }
    let shifted = if y >= 0 { y } else { y - 399 };
    let era = shifted / 400;
    let yoe = y - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146097 + doe - 719468
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let max_rooms = inst.int("max_rooms");
    let start: Vec<i64> = inst.strings("start_data").iter().map(|s| day_number(s)).collect();
    let end: Vec<i64> = inst.strings("end_data").iter().map(|s| day_number(s)).collect();
    let preassigned = inst.ints("preassigned_room_data"); // -1: no room given
    let n = start.len();

    // room_assignments[i] is the room (0..max_rooms-1) of request i.
    let room_assignments: Vec<Var> = (0..n)
        .map(|_| solver.new_bounded_integer(0, max_rooms - 1))
        .collect();

    // Some requests already have a room.
    let given = solver.new_constraint_tag();
    for i in 0..n {
        if preassigned[i] != -1 {
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![room_assignments[i].scaled(1)], preassigned[i], given))
                .post();
        }
    }

    // A room serves one request at a time. A request occupies its room on the
    // days from its start up to, but not including, its end, so two requests
    // share a day exactly when the later start is before the earlier end; such
    // requests get different rooms. (The reference states this per day as an
    // AllDifferent over the requests present that day; Pumpkin's all_different
    // is the same pairwise disequalities.)
    let different = solver.new_constraint_tag();
    for i in 0..n {
        for j in (i + 1)..n {
            if start[i].max(start[j]) < end[i].min(end[j]) {
                solver
                    .add_constraint(pumpkin_solver::not_equals(
                        vec![room_assignments[i].scaled(1), room_assignments[j].scaled(-1)], 0, different))
                    .post();
            }
        }
    }

    let mut m = Model::new();
    m.put("room_assignments", room_assignments);
    m
}
