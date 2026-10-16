Problem: choose the largest set of movies whose filming intervals [first day, last day] do not overlap; output selected_movies[i] = true when movie i (input order) is selected.
- "you cannot simultaneously accept two jobs whose intervals overlap" -> for every pair (i, j) whose intervals share a day (start_i <= end_j and start_j <= end_i): not (s_i and s_j) -> ~(s_i & s_j)
- "you seek the largest possible set of jobs" -> maximise the number of selected movies -> objective sum of s_i
- output selected_movies = the s_i in input order
