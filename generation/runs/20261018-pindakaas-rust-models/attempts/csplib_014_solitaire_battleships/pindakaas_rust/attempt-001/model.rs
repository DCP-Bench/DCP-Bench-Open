// CSPLib 014, Solitaire Battleships: place a fleet on a rows x cols grid so that the
// row and column sums and the hints hold. Satisfaction problem; the grid is the output.
//
// Modelling: each ship is a placement (a horizontal or vertical straight line of
// consecutive squares, or a single submarine square) with one selector literal.
// Placements that overlap or touch, including diagonally, cannot both be chosen.
// Each cell holds water when no chosen placement covers it, and otherwise the ship-part
// code of the placement that covers it. Ship counts per length come from the fleet.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let rows = inst.size("rows");
    let cols = inst.size("cols");
    let water = inst.int("WATER");
    let cl = inst.int("CIRCLE");
    let lf = inst.int("LEFT");
    let rt = inst.int("RIGHT");
    let tp = inst.int("TOP");
    let bt = inst.int("BOTTOM");
    let md = inst.int("MIDDLE");
    let ship_codes = [cl, lf, rt, tp, bt, md];
    let mut maxc = water;
    for &v in &ship_codes {
        maxc = maxc.max(v);
    }

    // Placements: one per (length, orientation, start square) that fits on the grid.
    // Each entry is (length, cells as (row, col, code)).
    struct Place {
        len: i64,
        cells: Vec<(usize, usize, i64)>,
        lit: Lit,
    }
    let fleet = inst.matrix("fleet_counts");
    let mut places: Vec<Place> = Vec::new();
    for f in &fleet {
        let k = f[0] as usize;
        let orientations: Vec<bool> = if k == 1 { vec![true] } else { vec![true, false] };
        for &horiz in &orientations {
            for r in 0..rows {
                for c in 0..cols {
                    let fits = if horiz { c + k <= cols } else { r + k <= rows };
                    if !fits {
                        continue;
                    }
                    let mut cells = Vec::new();
                    for i in 0..k {
                        let (rr, cc) = if horiz { (r, c + i) } else { (r + i, c) };
                        let code = if k == 1 {
                            cl
                        } else if i == 0 {
                            if horiz { lf } else { tp }
                        } else if i == k - 1 {
                            if horiz { rt } else { bt }
                        } else {
                            md
                        };
                        cells.push((rr, cc, code));
                    }
                    let lit = s.new_lit();
                    places.push(Place { len: f[0], cells, lit });
                }
            }
        }
    }

    // The ships do not overlap and do not touch, not even diagonally.
    // Two placements that overlap or come within one square of each other cannot both be chosen.
    for i in 0..places.len() {
        for j in (i + 1)..places.len() {
            let touch = places[i].cells.iter().any(|&(r1, c1, _)| {
                places[j].cells.iter().any(|&(r2, c2, _)| {
                    (r1 as i64 - r2 as i64).abs() <= 1 && (c1 as i64 - c2 as i64).abs() <= 1
                })
            });
            if touch {
                s.add_clause([!places[i].lit, !places[j].lit])?;
            }
        }
    }

    // Which placements cover each square, and with which ship-part code.
    let mut cover: Vec<Vec<Vec<(usize, i64)>>> = vec![vec![Vec::new(); cols]; rows];
    for (p, pl) in places.iter().enumerate() {
        for &(r, c, code) in &pl.cells {
            cover[r][c].push((p, code));
        }
    }

    // Each cell is one of water or the ship-part codes. The value literals of a cell's
    // integer variable are tied to the placements that cover it.
    let mut grid: Vec<Vec<IntVar>> = Vec::new();
    let mut water_lit: Vec<Vec<Lit>> = Vec::new();
    let mut val_lit: Vec<Vec<Vec<Lit>>> = Vec::new();
    for r in 0..rows {
        let mut grow = Vec::new();
        let mut wrow = Vec::new();
        let mut vrow = Vec::new();
        for c in 0..cols {
            let g = IntVar::new(0..=maxc);
            let mut eq: Vec<Lit> = Vec::new();
            for v in 0..=maxc {
                let b = g.equals(s, v)?;
                eq.push(lit_of(s, b)?);
            }
            // Values that are not water or a ship part are not allowed.
            for v in 0..=maxc {
                if v != water && !ship_codes.contains(&v) {
                    s.add_clause([!eq[v as usize]])?;
                }
            }
            let covers = &cover[r][c];
            // Water holds exactly when no chosen placement covers the square.
            let ew = eq[water as usize];
            for &(p, _) in covers {
                s.add_clause([!ew, !places[p].lit])?;
            }
            let mut none_covered: Vec<Lit> = covers.iter().map(|&(p, _)| places[p].lit).collect();
            none_covered.push(ew);
            s.add_clause(none_covered)?;
            // A ship-part code holds exactly when a chosen placement covers the square with that code.
            for &v in &ship_codes {
                let ev = eq[v as usize];
                let mut any: Vec<Lit> = vec![!ev];
                for &(p, code) in covers {
                    if code == v {
                        s.add_clause([!places[p].lit, ev])?;
                        any.push(places[p].lit);
                    }
                }
                s.add_clause(any)?;
            }
            grow.push(g);
            wrow.push(ew);
            vrow.push(eq);
        }
        grid.push(grow);
        water_lit.push(wrow);
        val_lit.push(vrow);
    }

    // Row and column sums: the number of ship squares in each row and column.
    let rowsum = inst.ints("rowsum");
    let colsum = inst.ints("colsum");
    for r in 0..rows {
        let mut e = LinExp::default();
        for c in 0..cols {
            e += LinExp::from(!water_lit[r][c]);
        }
        post(s, e, Comparator::Equal, rowsum[r])?;
    }
    for c in 0..cols {
        let mut e = LinExp::default();
        for r in 0..rows {
            e += LinExp::from(!water_lit[r][c]);
        }
        post(s, e, Comparator::Equal, colsum[c])?;
    }

    // The fleet: each ship length occurs exactly the given number of times.
    for f in &fleet {
        let k = f[0];
        let mut e = LinExp::default();
        for pl in places.iter().filter(|p| p.len == k) {
            e += LinExp::from(pl.lit);
        }
        post(s, e, Comparator::Equal, f[1])?;
    }

    // Hints: fixed squares, given as [row, col, code].
    if inst.has("hints") {
        for h in inst.matrix("hints") {
            let (r, c, code) = (h[0] as usize, h[1] as usize, h[2]);
            s.add_clause([val_lit[r][c][code as usize]])?;
        }
    }

    let mut out = Out::new();
    out.put("grid", &grid);
    Ok(out)
}
