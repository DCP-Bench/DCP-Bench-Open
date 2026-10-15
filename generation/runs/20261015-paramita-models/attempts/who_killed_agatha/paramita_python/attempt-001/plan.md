# Plan: who_killed_agatha, attempt-001

Requirement: someone in Dreadsbury Mansion killed Aunt Agatha; the killers are among Agatha, the butler and Charles.
-> killer_x one-hot Bools for x in {0,1,2}, exactly one true.

Requirement: a killer always hates his victim.
-> killer_x implies hates[x][Agatha].

Requirement: a killer is no richer than his victim.
-> killer_x implies not richer[x][Agatha]; richer is a strict partial order (irreflexive, transitive, asymmetric) over the three people.

Requirement: Charles hates no one that Agatha hates.
-> for each y: hates[Agatha][y] implies not hates[Charles][y].

Requirement: Agatha hates everybody except the butler.
-> hates[Agatha][y] is true for y != butler, false for the butler.

Requirement: the butler hates everyone not richer than Aunt Agatha.
-> for each y: not richer[y][Agatha] implies hates[butler][y].

Requirement: the butler hates everyone whom Agatha hates.
-> for each y: hates[Agatha][y] implies hates[butler][y].

Requirement: noone hates everyone.
-> for each x: at least one y with not hates[x][y].

Requirement: who killed Agatha (print the 0-based index).
-> output killer = sum(i * killer_i), integer expression.

Objective: none (satisfaction).
