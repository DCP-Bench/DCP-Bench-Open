// Age changing puzzle: find my age (m) and my husband's age (h).
//
// Ages are nonnegative integers. Four operations are available: +2, /8, -3, *7.
// Starting from my age and applying the four operations in some order gives
// my husband's age. Starting from his age and applying the same four operations
// in a different order gives my age.
//
// Division is exact: a /8 step is only allowed when the value divides evenly.
//
// Encoding: all 24 orders of the four operations are enumerated. For order k,
// a[k] holds when my age, put through order k, gives h. b[k] holds when his age,
// put through order k, gives m. Each step of an order is constrained only when
// its selector holds, so a selector that is false leaves its chain free.

const AGE_HI: i64 = 1_000;
const LO: i64 = -10_000;
const HI: i64 = 10_000;

// All orders of the operations 0..4 (0: +2, 1: /8, 2: -3, 3: *7).
fn orders() -> Vec<[usize; 4]> {
    let mut out = Vec::new();
    for a in 0..4 {
        for b in 0..4 {
            for c in 0..4 {
                for d in 0..4 {
                    let p = [a, b, c, d];
                    let mut seen = [false; 4];
                    let mut ok = true;
                    for &x in &p {
                        if seen[x] {
                            ok = false;
                        }
                        seen[x] = true;
                    }
                    if ok {
                        out.push(p);
                    }
                }
            }
        }
    }
    out
}

// One step: y is x after operation `op`, enforced when `on` holds.
// Operations: 0 is +2, 1 is /8 (exact), 2 is -3, 3 is *7.
fn step(m: &mut Model, x: View<i64>, op: usize, on: View<bool>) -> Res<View<i64>> {
    let y = m.new_int_decision(LO..=HI);
    match op {
        0 => {
            // y is x plus 2
            m.linear(x - y).eq(-2).implied_by(on).post()?;
        }
        1 => {
            // y is x divided by 8, with no remainder: x is 8 times y
            m.linear(x - y * 8).le(0).implied_by(on).post()?;
            m.linear(x - y * 8).ge(0).implied_by(on).post()?;
        }
        2 => {
            // y is x minus 3
            m.linear(x - y).eq(3).implied_by(on).post()?;
        }
        _ => {
            // y is x times 7: y is 7 times x
            m.linear(x * 7 - y).le(0).implied_by(on).post()?;
            m.linear(x * 7 - y).ge(0).implied_by(on).post()?;
        }
    }
    Ok(y)
}

// Apply the operations of `order`, one after another, starting from `start`.
fn chain(m: &mut Model, start: View<i64>, order: &[usize; 4], on: View<bool>) -> Res<View<i64>> {
    let mut cur = start;
    for &op in order {
        cur = step(m, cur, op, on)?;
    }
    Ok(cur)
}

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let mine = m.new_int_decision(0..=AGE_HI);
    let husband = m.new_int_decision(0..=AGE_HI);
    let orders = orders();

    let mut a: Vec<View<bool>> = Vec::new();
    let mut b: Vec<View<bool>> = Vec::new();
    for _ in &orders {
        a.push(m.new_bool_decision());
        b.push(m.new_bool_decision());
    }

    // If you start with my age, in years, and apply the four operations in some order,
    // then the final answer you get is my husband's age.
    for (k, order) in orders.iter().enumerate() {
        let on = a[k];
        let end = chain(m, mine, order, on)?;
        m.linear(end - husband).le(0).implied_by(on).post()?;
        m.linear(end - husband).ge(0).implied_by(on).post()?;
    }

    // Some order must give my husband's age from my age.
    m.linear(a.iter().copied().sum::<IntLinearExp>()).ge(1).post()?;

    // If you start with his age and apply the same four operations in a different order,
    // then you get my age.
    for (k, order) in orders.iter().enumerate() {
        let on = b[k];
        let end = chain(m, husband, order, on)?;
        m.linear(end - mine).le(0).implied_by(on).post()?;
        m.linear(end - mine).ge(0).implied_by(on).post()?;
    }

    // Some order must give my age from his age.
    m.linear(b.iter().copied().sum::<IntLinearExp>()).ge(1).post()?;

    // The order that gives his age from mine and the order that gives mine from his must differ.
    for k in 0..orders.len() {
        m.linear([a[k], b[k]].iter().copied().sum::<IntLinearExp>()).le(1).post()?;
    }

    let mut out = Out::new();
    out.put("h", husband).put("m", mine);
    Ok(out)
}
