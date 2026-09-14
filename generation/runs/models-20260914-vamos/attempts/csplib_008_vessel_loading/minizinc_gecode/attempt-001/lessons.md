Gecode solves the embedded 5 x 5 instance in under two seconds but hits the
180 s execution budget on the 16 x 16 / 10-container instance, whose containers
fill the deck exactly. Attempts 002 and 003 added the implied `diffn` and
`cumulative` constraints for that pair (002 failed outright because Gecode's
`cumulative` rejects durations whose declared domain is not non-negative; 003
fixed the declarations). Attempt 003 still timed out on the same instance, so
the extra constraints bought nothing here and attempt 001, the direct
translation of the reference, is the one retained. The coverage claim for this
model is therefore the example instance only.
