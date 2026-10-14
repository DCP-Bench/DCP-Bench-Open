from pycsp3 import *

# Choose the largest set of movie offers whose filming periods do not overlap.
# Each offer is [title, first day, last day]; the film days are inclusive, so two
# offers conflict when they share a day.

movies = data.movies
n = len(movies)
first_day = [m[1] for m in movies]
last_day = [m[2] for m in movies]

# selected_movies[i] is 1 when offer i is accepted
selected_movies = VarArray(size=n, dom={0, 1})

satisfy(
    # two offers whose filming periods overlap cannot both be accepted
    [selected_movies[i] + selected_movies[j] <= 1
     for i in range(n) for j in range(i + 1, n)
     if first_day[i] <= last_day[j] and first_day[j] <= last_day[i]],
)

# maximise the number of accepted offers
maximize(Sum(selected_movies))
