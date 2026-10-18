// Problem initials_queue: the initials of the first 10 people in a queue for a Maths lecture.
// Letters A to E are coded 0 to 4. Output queue[i] = [first, second] for the i-th person
// from the front.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    const N: usize = 10;
    const LAST: i64 = 4;

    // Each of them had initials which were an alphabetically ordered pair of distinct
    // letters from the first five letters of the alphabet (A,B,C,D,E).
    let mut queue: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..N {
        let first = m.new_int_decision(0..=LAST);
        let second = m.new_int_decision(0..=LAST);
        m.linear(first - second).le(-1).post()?;
        queue.push(vec![first, second]);
    }

    // None of the people had the same initials as any other.
    let mut codes = Vec::new();
    for person in &queue {
        let code = m.new_int_decision(0..=(LAST * 5 + LAST));
        m.linear(person[0] * 5 + person[1]).eq(code).post()?;
        codes.push(code);
    }
    m.unique(codes.clone()).post()?;

    // No-one shared a letter with the person in front of them.
    for i in 0..N - 1 {
        for u in 0..2 {
            for v in 0..2 {
                m.linear(queue[i][u] - queue[i + 1][v]).ne(0).post()?;
            }
        }
    }

    // Mathematician BE was at the front of the queue with CD right behind,
    // while BD was right at the end of the queue.
    m.linear(queue[0][0]).eq(1).post()?;
    m.linear(queue[0][1]).eq(4).post()?;
    m.linear(queue[1][0]).eq(2).post()?;
    m.linear(queue[1][1]).eq(3).post()?;
    m.linear(queue[N - 1][0]).eq(1).post()?;
    m.linear(queue[N - 1][1]).eq(3).post()?;

    let mut out = Out::new();
    out.put("queue", queue);
    Ok(out)
}
