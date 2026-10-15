#include "dcp.h"

// Movie scheduling (weighted interval scheduling with unit weights): the actor
// is offered n films, each with a first and last day of filming. Accept the
// largest set of films such that no two accepted films share a filming day.
class MovieScheduling : public dcp::Space {
 protected:
  BoolVarArray selected_movies;  // selected_movies[i] = 1 if film i is accepted
  IntVar total;                  // number of accepted films (objective)

 public:
  explicit MovieScheduling(const json& instance) {
    const auto& movies = instance.at("movies");
    int n = static_cast<int>(movies.size());

    selected_movies = BoolVarArray(*this, n, 0, 1);

    // The actor is one resource: an accepted film occupies the actor from its
    // first day to its last day, both included, so its duration is last - first + 1.
    // Two films that share a day cannot both run on the resource, which is the
    // overlap rule of the description.
    IntVarArgs start;
    IntArgs duration(n);
    BoolVarArgs accepted;
    for (int i = 0; i < n; ++i) {
      int first = movies[i][1].get<int>();
      int last = movies[i][2].get<int>();
      // the film's first day is fixed by the offer
      start << IntVar(*this, first, first);
      duration[i] = last - first + 1;
      accepted << selected_movies[i];
    }
    // no two accepted films overlap (unary resource with optional tasks)
    unary(*this, start, duration, accepted, IPL_DEF);

    // maximise the number of accepted films, since every film pays the same fee
    total = expr(*this, sum(accepted));
    maximize(total);

    // try to accept each film first, then the rest of the search is forced by the resource
    branch(*this, selected_movies, BOOL_VAR_NONE(), BOOL_VAL_MAX());
    output("selected_movies", selected_movies);
  }

  MovieScheduling(MovieScheduling& s) : dcp::Space(s) {
    selected_movies.update(*this, s.selected_movies);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new MovieScheduling(*this); }
};

DCP_MODEL(MovieScheduling)
