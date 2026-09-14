Attempt 001 failed with `existence_error(procedure, maplist/7)`: SWI-Prolog's
maplist goes up to maplist/5, that is a goal and four lists, and this model
walked six lists at once. Attempt 002 maps over the container indices instead
and reads each list with nth1/3, which is the shape to reach for whenever a
model needs more than four parallel lists.
