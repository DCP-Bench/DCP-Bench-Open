# session2_movie_scheduling plan

- "you must commit to being available throughout this entire period" / "Each offer comes specified with the first and last day of filming" -> movies[i] = [title, first day, last day], read from raw movies; days are inclusive
- "you cannot simultaneously accept two jobs whose intervals overlap" -> for each day d that some film starts, sum of selected films covering d <= 1 (clique cover of the interval graph) via m.sum(..., "<=", 1)
- "Print which movies are accepted (selected_movies) as a list of booleans" -> sel[i] BoolVar; out.put("selected_movies", sel)
- "you seek the largest possible set of jobs" -> count = sum of sel, setObjective MAXIMIZE
