Four islands, each with a different name -> island[k] = map position (A=0, B=1, C=2, D=3), allDifferent over the four islands.
Each island has a different primary export -> export[e] = map position, allDifferent over the four exports.
Each island has a different tourist attraction -> attraction[a] = map position, allDifferent over the four attractions.
Map: A-B east-west bridge, A-C north-south bridge, B-D north-south bridge, C-D east-west bridge; positions as the pair table of the relation.
1. The koala preserve island is due south of Pwana -> table(island[Pwana], attraction[koala]) with (A,C),(B,D).
2. The alabaster island is due west of Quero -> table(export[alabaster], island[Quero]) with (A,B),(C,D).
3. The resort hotel island is due east of the durian island -> table(export[durian], attraction[hotel]) with (A,B),(C,D).
4. Skern and the jai alai island are connected by a north-south bridge -> table(island[Skern], attraction[jai alai]) with (A,C),(C,A),(B,D),(D,B).
5. Rayou and the banana island are connected by an east-west bridge -> table(island[Rayou], export[bananas]) with (A,B),(B,A),(C,D),(D,C).
6. Ice skating rink and jai alai stadium are not connected by a bridge -> table(attraction[ice], attraction[jai alai]) with the diagonals (A,D),(D,A),(B,C),(C,B).
Objective: satisfaction, no objective.
