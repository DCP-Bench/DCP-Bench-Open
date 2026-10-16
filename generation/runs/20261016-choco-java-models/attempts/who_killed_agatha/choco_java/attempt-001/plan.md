Someone in Dreadsbury Mansion killed Aunt Agatha. (killer is one of 0..n-1)
Agatha, the butler, and Charles live in Dreadsbury Mansion (3 persons, killer domain 0..2)
A killer always hates, and is no richer than his victim. (killer hates Agatha: element over hates[.][0]; killer not richer than Agatha: element over richer[.][0] = 0)
Charles hates noone that Agatha hates. -> hates[A][x] + hates[C][x] <= 1 for all x
Agatha hates everybody except the butler. -> hates[A][x] = 1 for x != butler, hates[A][butler] = 0
The butler hates everyone not richer than Aunt Agatha. -> richer[x][A] + hates[B][x] >= 1 for all x
The butler hates everyone whom Agatha hates. -> hates[A][x] <= hates[B][x] for all x
Noone hates everyone. -> sum_y hates[x][y] <= n-1 for all x
Who killed Agatha? (objective) -> satisfaction, output killer
