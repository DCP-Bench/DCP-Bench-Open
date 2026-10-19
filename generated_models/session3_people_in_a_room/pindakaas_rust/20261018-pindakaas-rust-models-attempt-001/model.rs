// Problem: session3_people_in_a_room.
// 13 people, 4 of them male, enter a room one at a time. Find an order of entry
// so that the ratio of females to males in the room at any one time is no greater
// than 7/3. Output the sequence: 0 for male, 1 for female.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n: usize = 13;
    let males: i64 = 4;
    let females: i64 = n as i64 - males;

    // female[i] is true when the person entering at position i is female.
    let mut female: Vec<Lit> = Vec::new();
    for _ in 0..n {
        female.push(s.new_lit());
    }

    // There are 13 people. 4 of them are male.
    let mut total = LinExp::default();
    for f in &female {
        total += LinExp::from(f.clone());
    }
    post(s, total, Comparator::Equal, females)?;

    // The ratio of females to males in the room at any one time is no greater than 7/3.
    // With F females and M males in the room, F/M <= 7/3 is 3F <= 7M, which is
    // 10F <= 7t for t = F + M people in the room. This also forces no female before
    // the first male, since M = 0 needs F = 0.
    for t in 1..=n {
        let mut in_room = LinExp::default();
        for f in female.iter().take(t) {
            in_room += LinExp::from(f.clone()) * 10;
        }
        post(s, in_room, Comparator::LessEq, 7 * t as i64)?;
    }

    // Print the sequence of people entering the room, 0 male and 1 female.
    let mut out = Out::new();
    out.put("sequence", &female);
    Ok(out)
}
