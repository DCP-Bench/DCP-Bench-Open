// Crossfigures (csplib 021): fill a numerical crossword. The grid has black cells and
// white cells; each white cell takes one digit. Each run of two or more white cells across
// or down is a number read from its digits, left to right or top to bottom, with no leading
// zero. The clues below fix relations between these numbers.
// Output M is the 9x9 grid of digits, with 0 in the black cells.

use std::collections::HashMap;

// 0 = black cell, -1 = white cell without a clue number, k > 0 = white cell numbered k.
const GRID: [[i64; 9]; 9] = [
    [1, 2, -1, 3, 0, 4, -1, 5, 6],
    [7, -1, 0, 8, -1, -1, 0, 9, -1],
    [-1, 0, 10, -1, 0, 11, 12, 0, -1],
    [13, 14, -1, -1, 0, 15, -1, 16, -1],
    [0, -1, 0, 0, 0, 0, 0, -1, 0],
    [17, -1, 18, 19, 0, 20, 21, -1, 22],
    [-1, 0, 23, -1, 0, 24, -1, 0, -1],
    [25, 26, 0, 27, -1, -1, 0, 28, -1],
    [29, -1, -1, -1, 0, 30, -1, -1, -1],
];

fn is_prime(n: i64) -> bool {
    n >= 2 && (2..n).take_while(|d| d * d <= n).all(|d| n % d != 0)
}

// The rows of a table that fix a number to the k-th powers in lo..=hi.
fn powers_in(lo: i64, hi: i64) -> Vec<Vec<i64>> {
    (1i64..=100).filter(|k| (lo..=hi).contains(&(k * k))).map(|k| vec![k * k]).collect()
}

// A number written by the digits in `cells` (most significant first), with no leading zero.
fn entry(s: &mut Cadical, cells: &[IntVar]) -> Res<IntVar> {
    let len = cells.len() as u32;
    let z = IntVar::new(10i64.pow(len - 1)..=(10i64.pow(len) - 1));
    let mut e = LinExp::default();
    for (i, d) in cells.iter().enumerate() {
        e += scaled(d, 10i64.pow(len - 1 - i as u32));
    }
    post(s, e - iv(&z), Comparator::Equal, 0)?;
    Ok(z)
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The grid and the clues come from the problem statement; the instance has no data.
    let mut cell: Vec<Vec<IntVar>> = Vec::new();
    for r in 0..9 {
        let mut row = Vec::new();
        for c in 0..9 {
            row.push(if GRID[r][c] == 0 { IntVar::new(0..=0) } else { IntVar::new(0..=9) });
        }
        cell.push(row);
    }

    // One variable per across and per down entry: a run of white cells, keyed by its clue number.
    let mut across: HashMap<i64, IntVar> = HashMap::new();
    let mut down: HashMap<i64, IntVar> = HashMap::new();
    for r in 0..9 {
        for c in 0..9 {
            if GRID[r][c] == 0 {
                continue;
            }
            if (c == 0 || GRID[r][c - 1] == 0) && c + 1 < 9 && GRID[r][c + 1] != 0 {
                let mut run = Vec::new();
                let mut k = c;
                while k < 9 && GRID[r][k] != 0 {
                    run.push(cell[r][k].clone());
                    k += 1;
                }
                across.insert(GRID[r][c], entry(s, &run)?);
            }
            if (r == 0 || GRID[r - 1][c] == 0) && r + 1 < 9 && GRID[r + 1][c] != 0 {
                let mut run = Vec::new();
                let mut k = r;
                while k < 9 && GRID[k][c] != 0 {
                    run.push(cell[k][c].clone());
                    k += 1;
                }
                down.insert(GRID[r][c], entry(s, &run)?);
            }
        }
    }
    let a = |k: i64| &across[&k];
    let d = |k: i64| &down[&k];

    // Across 1: 27 across times two
    post(s, iv(a(1)) - scaled(a(27), 2), Comparator::Equal, 0)?;
    // Across 4: 4 down plus seventy-one
    post(s, iv(a(4)) - iv(d(4)), Comparator::Equal, 71)?;
    // Across 7: 18 down plus four
    post(s, iv(a(7)) - iv(d(18)), Comparator::Equal, 4)?;
    // Across 8: 6 down divided by sixteen
    post(s, iv(d(6)) - scaled(a(8), 16), Comparator::Equal, 0)?;
    // Across 9: 2 down minus eighteen
    post(s, iv(a(9)) - iv(d(2)), Comparator::Equal, -18)?;
    // Across 10: Dozen in six gross (six gross is 864, and 864 / 12 = 72)
    post(s, iv(a(10)), Comparator::Equal, 72)?;
    // Across 11: 5 down minus seventy
    post(s, iv(a(11)) - iv(d(5)), Comparator::Equal, -70)?;
    // Across 13: 26 down times 23 across
    times(s, a(23), d(26), a(13))?;
    // Across 15: 6 down minus 350
    post(s, iv(a(15)) - iv(d(6)), Comparator::Equal, -350)?;
    // Across 17: 25 across times 23 across
    times(s, a(23), a(25), a(17))?;
    // Across 20: A square number
    table(s, std::slice::from_ref(a(20)), &powers_in(1000, 9999))?;
    // Across 23: A prime number
    let primes: Vec<Vec<i64>> = (10..100).filter(|&n| is_prime(n)).map(|n| vec![n]).collect();
    table(s, std::slice::from_ref(a(23)), &primes)?;
    // Across 24: A square number
    table(s, std::slice::from_ref(a(24)), &powers_in(10, 99))?;
    // Across 25: 20 across divided by seventeen
    post(s, iv(a(20)) - scaled(a(25), 17), Comparator::Equal, 0)?;
    // Across 27: 6 down divided by four
    post(s, iv(d(6)) - scaled(a(27), 4), Comparator::Equal, 0)?;
    // Across 28: Four dozen (48)
    post(s, iv(a(28)), Comparator::Equal, 48)?;
    // Across 29: Seven gross (7 * 144 = 1008)
    post(s, iv(a(29)), Comparator::Equal, 1008)?;
    // Across 30: 22 down plus 450
    post(s, iv(a(30)) - iv(d(22)), Comparator::Equal, 450)?;

    // Down 1: 1 across plus twenty-seven
    post(s, iv(d(1)) - iv(a(1)), Comparator::Equal, 27)?;
    // Down 2: Five dozen (60)
    post(s, iv(d(2)), Comparator::Equal, 60)?;
    // Down 3: 30 across plus 888
    post(s, iv(d(3)) - iv(a(30)), Comparator::Equal, 888)?;
    // Down 4: Two times 17 across
    post(s, iv(d(4)) - scaled(a(17), 2), Comparator::Equal, 0)?;
    // Down 5: 29 across divided by twelve
    post(s, iv(a(29)) - scaled(d(5), 12), Comparator::Equal, 0)?;
    // Down 6: 28 across times 23 across (28 across is 48)
    post(s, iv(d(6)) - scaled(a(23), 48), Comparator::Equal, 0)?;
    // Down 10: 10 across plus four
    post(s, iv(d(10)) - iv(a(10)), Comparator::Equal, 4)?;
    // Down 12: Three times 24 across
    post(s, iv(d(12)) - scaled(a(24), 3), Comparator::Equal, 0)?;
    // Down 14: 13 across divided by sixteen
    post(s, iv(a(13)) - scaled(d(14), 16), Comparator::Equal, 0)?;
    // Down 16: 28 down times fifteen
    post(s, iv(d(16)) - scaled(d(28), 15), Comparator::Equal, 0)?;
    // Down 17: 13 across minus 399
    post(s, iv(d(17)) - iv(a(13)), Comparator::Equal, -399)?;
    // Down 18: 29 across divided by eighteen
    post(s, iv(a(29)) - scaled(d(18), 18), Comparator::Equal, 0)?;
    // Down 19: 22 down minus ninety-four
    post(s, iv(d(19)) - iv(d(22)), Comparator::Equal, -94)?;
    // Down 20: 20 across minus nine
    post(s, iv(d(20)) - iv(a(20)), Comparator::Equal, -9)?;
    // Down 21: 25 across minus fifty-two
    post(s, iv(d(21)) - iv(a(25)), Comparator::Equal, -52)?;
    // Down 22: 20 down times six
    post(s, iv(d(22)) - scaled(d(20), 6), Comparator::Equal, 0)?;
    // Down 26: Five times 24 across
    post(s, iv(d(26)) - scaled(a(24), 5), Comparator::Equal, 0)?;
    // Down 28: 21 down plus twenty-seven
    post(s, iv(d(28)) - iv(d(21)), Comparator::Equal, 27)?;

    let mut out = Out::new();
    out.put("M", &cell);
    Ok(out)
}
