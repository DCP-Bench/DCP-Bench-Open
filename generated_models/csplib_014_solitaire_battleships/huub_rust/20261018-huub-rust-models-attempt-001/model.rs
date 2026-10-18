// Solitaire battleships (CSPLib prob014) on the instance's rows x cols grid.
// Each cell is water, a submarine (CIRCLE), or a ship part (LEFT, RIGHT, TOP,
// BOTTOM, MIDDLE). The fleet has battleships (length 4), cruisers (length 3),
// destroyers (length 2) and submarines (length 1); fleet_counts gives how many
// of each as [length, count]. Ships are horizontal or vertical, and no two ships
// touch, not even diagonally. rowsum and colsum count the occupied squares of
// each row and column. hints fix cells as [row, col, code].

// For each cell and each code, the literal "the cell takes this code"; None for
// the code _SHIP, which no cell takes.
type Grid = Vec<Vec<Vec<Option<View<bool>>>>>;

fn clause(m: &mut Model, lits: &[View<bool>]) -> Res<()> {
    let mut f = BoolFormula::Atom(lits[0]);
    for &l in &lits[1..] {
        f = f | BoolFormula::Atom(l);
    }
    m.proposition(f).post()?;
    Ok(())
}

// If the cell (r, c) takes code x (and `extra` holds, when given), then the
// neighbour at offset (dr, dc) takes one of the codes in ys. Outside the grid
// counts as water.
#[allow(clippy::too_many_arguments)]
fn req(
    m: &mut Model,
    is: &Grid,
    water: i64,
    r: usize,
    c: usize,
    x: i64,
    dr: i64,
    dc: i64,
    ys: &[i64],
    extra: Option<View<bool>>,
) -> Res<()> {
    let nr = r as i64 + dr;
    let nc = c as i64 + dc;
    let mut lits = vec![!is[r][c][x as usize].unwrap()];
    if let Some(e) = extra {
        lits.push(e);
    }
    if nr < 0 || nc < 0 || nr as usize >= is.len() || nc as usize >= is[0].len() {
        if ys.contains(&water) {
            return Ok(());
        }
    } else {
        for &y in ys {
            if let Some(l) = is[nr as usize][nc as usize][y as usize] {
                lits.push(l);
            }
        }
    }
    clause(m, &lits)
}

fn cells_with(is: &Grid, code: i64) -> Vec<View<bool>> {
    let mut v = Vec::new();
    for row in is {
        for cell in row {
            if let Some(l) = cell[code as usize] {
                v.push(l);
            }
        }
    }
    v
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let rows = inst.size("rows");
    let cols = inst.size("cols");
    let water = inst.int("WATER");
    let sub = inst.int("CIRCLE");
    let left = inst.int("LEFT");
    let right = inst.int("RIGHT");
    let top = inst.int("TOP");
    let bottom = inst.int("BOTTOM");
    let middle = inst.int("MIDDLE");
    let ship = inst.int("_SHIP");
    let hi = [water, sub, left, right, top, bottom, middle]
        .into_iter()
        .max()
        .unwrap_or(0);

    // The grid: one cell variable per square, with the codes of the instance.
    let mut cells: Vec<Vec<View<i64>>> = Vec::with_capacity(rows);
    for _ in 0..rows {
        cells.push(m.new_int_decisions(cols, 0..=hi));
    }
    for r in 0..rows {
        for c in 0..cols {
            m.linear(cells[r][c]).ne(ship).post()?;
        }
    }
    let mut is: Grid = vec![vec![vec![None; hi as usize + 1]; cols]; rows];
    for r in 0..rows {
        for c in 0..cols {
            for k in 0..=hi {
                if k != ship {
                    is[r][c][k as usize] = Some(m.linear(cells[r][c]).eq(k).reify());
                }
            }
        }
    }
    let mut hz: Vec<Vec<View<bool>>> = Vec::with_capacity(rows);
    for _ in 0..rows {
        hz.push((0..cols).map(|_| m.new_bool_decision()).collect());
    }

    // The hints fix some squares.
    for h in inst.matrix("hints") {
        m.linear(cells[h[0] as usize][h[1] as usize]).eq(h[2]).post()?;
    }

    // Ships are straight, and no two ships touch, not even diagonally: every
    // ship square has water on its four diagonals.
    // Each ship part has the right neighbours for its place in its ship.
    let w = [water];
    for r in 0..rows {
        for c in 0..cols {
            for x in [sub, left, right, top, bottom, middle] {
                for (dr, dc) in [(-1, -1), (-1, 1), (1, -1), (1, 1)] {
                    req(m, &is, water, r, c, x, dr, dc, &w, None)?;
                }
            }
            // A submarine is a single square: water all around it.
            for (dr, dc) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
                req(m, &is, water, r, c, sub, dr, dc, &w, None)?;
            }
            // A left end has water above, below and to its left, and a right part
            // (right or middle) to its right.
            req(m, &is, water, r, c, left, -1, 0, &w, None)?;
            req(m, &is, water, r, c, left, 1, 0, &w, None)?;
            req(m, &is, water, r, c, left, 0, -1, &w, None)?;
            req(m, &is, water, r, c, left, 0, 1, &[right, middle], None)?;
            // A right end is mirrored.
            req(m, &is, water, r, c, right, -1, 0, &w, None)?;
            req(m, &is, water, r, c, right, 1, 0, &w, None)?;
            req(m, &is, water, r, c, right, 0, 1, &w, None)?;
            req(m, &is, water, r, c, right, 0, -1, &[left, middle], None)?;
            // A top end has water above, left and right, and a vertical part below.
            req(m, &is, water, r, c, top, -1, 0, &w, None)?;
            req(m, &is, water, r, c, top, 0, -1, &w, None)?;
            req(m, &is, water, r, c, top, 0, 1, &w, None)?;
            req(m, &is, water, r, c, top, 1, 0, &[bottom, middle], None)?;
            // A bottom end is mirrored.
            req(m, &is, water, r, c, bottom, 1, 0, &w, None)?;
            req(m, &is, water, r, c, bottom, 0, -1, &w, None)?;
            req(m, &is, water, r, c, bottom, 0, 1, &w, None)?;
            req(m, &is, water, r, c, bottom, -1, 0, &[top, middle], None)?;
            // A middle part is horizontal (hz true) or vertical (hz false).
            let h = hz[r][c];
            req(m, &is, water, r, c, middle, -1, 0, &w, Some(!h))?;
            req(m, &is, water, r, c, middle, 1, 0, &w, Some(!h))?;
            req(m, &is, water, r, c, middle, 0, -1, &[left, middle], Some(!h))?;
            req(m, &is, water, r, c, middle, 0, 1, &[right, middle], Some(!h))?;
            req(m, &is, water, r, c, middle, 0, -1, &w, Some(h))?;
            req(m, &is, water, r, c, middle, 0, 1, &w, Some(h))?;
            req(m, &is, water, r, c, middle, -1, 0, &[top, middle], Some(h))?;
            req(m, &is, water, r, c, middle, 1, 0, &[bottom, middle], Some(h))?;
        }
    }

    // The row and column sums count the occupied squares.
    let rowsum = inst.ints("rowsum");
    let colsum = inst.ints("colsum");
    for r in 0..rows {
        let occupied: Vec<View<bool>> = (0..cols).map(|c| !is[r][c][water as usize].unwrap()).collect();
        m.linear(occupied.into_iter().sum::<IntLinearExp>()).eq(rowsum[r]).post()?;
    }
    for c in 0..cols {
        let occupied: Vec<View<bool>> = (0..rows).map(|r| !is[r][c][water as usize].unwrap()).collect();
        m.linear(occupied.into_iter().sum::<IntLinearExp>()).eq(colsum[c]).post()?;
    }

    // The fleet: the number of ships of each length, from fleet_counts.
    // A submarine is one CIRCLE square. A battleship has two adjacent middle
    // squares, and a cruiser has one middle square. A ship of length 2 or more
    // has one left or top end. Those counts fix the fleet.
    let fleet = inst.matrix("fleet_counts");
    let count_of = |len: i64| -> i64 { fleet.iter().find(|e| e[0] == len).map_or(0, |e| e[1]) };
    let battleships = count_of(4);
    let cruisers = count_of(3);
    let destroyers = count_of(2);
    let submarines = count_of(1);

    m.linear(cells_with(&is, sub).into_iter().sum::<IntLinearExp>())
        .eq(submarines)
        .post()?;

    // Two adjacent middle squares lie in a battleship, and only there.
    let mut pairs: Vec<View<bool>> = Vec::new();
    for r in 0..rows {
        for c in 0..cols {
            if c + 1 < cols {
                let (p, q) = (is[r][c][middle as usize].unwrap(), is[r][c + 1][middle as usize].unwrap());
                pairs.push(m.linear(vec![p, q].into_iter().sum::<IntLinearExp>()).ge(2).reify());
            }
            if r + 1 < rows {
                let (p, q) = (is[r][c][middle as usize].unwrap(), is[r + 1][c][middle as usize].unwrap());
                pairs.push(m.linear(vec![p, q].into_iter().sum::<IntLinearExp>()).ge(2).reify());
            }
        }
    }
    m.linear(pairs.into_iter().sum::<IntLinearExp>()).eq(battleships).post()?;

    // Middle squares: two per battleship, one per cruiser.
    m.linear(cells_with(&is, middle).into_iter().sum::<IntLinearExp>())
        .eq(2 * battleships + cruisers)
        .post()?;

    // Ships of length 2 or more: one left or top end each.
    let mut ends = cells_with(&is, left);
    ends.extend(cells_with(&is, top));
    m.linear(ends.into_iter().sum::<IntLinearExp>())
        .eq(battleships + cruisers + destroyers)
        .post()?;

    let mut out = Out::new();
    out.put("grid", cells);
    Ok(out)
}
