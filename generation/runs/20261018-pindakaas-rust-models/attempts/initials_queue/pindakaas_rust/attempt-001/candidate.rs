// Problem: initials_queue. Ten people stand in a queue for a Maths lecture. Each
// has initials that are an alphabetically ordered pair of distinct letters from
// A..E (0..4 here). No two people have the same initials, and no person shares a
// letter with the person directly in front. The front (position 0) is BE, position
// 1 is CD, and the last position (9) is BD. Output: queue[p] = [first, second]
// letter of the person at position p, from the front.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    const N: usize = 10;
    const LETTERS: i64 = 5;

    // The two letters of each person's initials, each in 0..4 (A=0 ... E=4).
    let mut a: Vec<IntVar> = Vec::new();
    let mut b: Vec<IntVar> = Vec::new();
    for _ in 0..N {
        a.push(IntVar::new(0..=LETTERS - 1));
        b.push(IntVar::new(0..=LETTERS - 1));
    }

    // initials are an alphabetically ordered pair of distinct letters: first < second
    for p in 0..N {
        post(s, iv(&a[p]) - iv(&b[p]), Comparator::LessEq, -1)?;
    }

    // none of the people had the same initials as any other person:
    // the code 5 * first + second identifies the pair, and the codes are all different
    let mut codes: Vec<IntVar> = Vec::new();
    for p in 0..N {
        codes.push(define(s, scaled(&a[p], 5) + iv(&b[p]))?);
    }
    all_different(s, &codes)?;

    // membership literals: letter l is one of the two initials of person p
    let mut in_first: Vec<Vec<Lit>> = Vec::new();
    let mut in_second: Vec<Vec<Lit>> = Vec::new();
    for p in 0..N {
        let mut f = Vec::new();
        let mut g = Vec::new();
        for l in 0..LETTERS as usize {
            f.push(reify_eq(s, iv(&a[p]), l as i64)?);
            g.push(reify_eq(s, iv(&b[p]), l as i64)?);
        }
        in_first.push(f);
        in_second.push(g);
    }

    // no-one shared a letter with the person in front of them: for each letter,
    // a person and the person directly behind may not both have it
    for p in 0..N - 1 {
        for l in 0..LETTERS as usize {
            for x in [in_first[p][l], in_second[p][l]] {
                for y in [in_first[p + 1][l], in_second[p + 1][l]] {
                    s.add_clause([!x, !y])?;
                }
            }
        }
    }

    // Mathematician BE was at the front of the queue: first = B (1), second = E (4)
    post(s, iv(&a[0]), Comparator::Equal, 1)?;
    post(s, iv(&b[0]), Comparator::Equal, 4)?;

    // with CD right behind: first = C (2), second = D (3)
    post(s, iv(&a[1]), Comparator::Equal, 2)?;
    post(s, iv(&b[1]), Comparator::Equal, 3)?;

    // BD was right at the end of the queue: first = B (1), second = D (3)
    post(s, iv(&a[N - 1]), Comparator::Equal, 1)?;
    post(s, iv(&b[N - 1]), Comparator::Equal, 3)?;

    let mut queue: Vec<Vec<IntVar>> = Vec::new();
    for p in 0..N {
        queue.push(vec![a[p].clone(), b[p].clone()]);
    }
    let mut out = Out::new();
    out.put("queue", &queue);
    Ok(out)
}
