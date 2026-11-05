A tiny nation in the South Pacific contains four islands connected by bridges
as shown (see below). Each of the four islands (Pwana, Quero, Rayou, and Skern)
boasts a different primary export (alabaster, bananas, coconuts, and durian
fruit) and a different tourist attraction (hotel, ice skating rink, jai alai
stadium, and koala preserve). Can you find the name, export, and tourist
attraction of each island on the map?

A, B, C, D are the islands, this is the map showing the bridges and the orientation of the islands:

```text
(A) -- (B)
 |      |
 |      |
(C) -- (D)
```

This means that A is north of C, C is west of D, etc.

1. The island noted for its koala preserve is due south of Pwana.
2. The island with the largest alabaster quarry is due west of Quero.
3. The island with the resort hotel is due east of the one that exports
   durian fruit.
4. Skern and the island with the jai alai stadium are connected by a
   north-south bridge.
5. Rayou and the island that exports bananas are connected by an east-west
   bridge.
6. The islands noted for the South Pacific's largest ice skating rink and
   for the jai alai stadium are not connected by a bridge.

Determine: Island name -- Export -- Tourist Attraction

Print a number for each island (island), export (export), and attraction (attraction) as three lists of integers from 0
to 3. The value at each index is the map position of that item, encoded as A=0, B=1, C=2, D=3. The list indices refer
respectively to: island = [Pwana, Quero, Rayou, Skern], export = [alabaster, bananas, coconuts, durian_fruit],
attraction = [resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve].
