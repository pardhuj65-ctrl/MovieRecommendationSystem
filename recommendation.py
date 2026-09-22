import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# LOAD LOCAL MOVIE DATA
# ============================================================

movies = pd.read_csv("movies.csv")

for column in ["title", "genre", "description", "rating"]:
    if column not in movies.columns:
        movies[column] = ""

movies["title"] = movies["title"].fillna("").astype(str)
movies["genre"] = movies["genre"].fillna("").astype(str)
movies["description"] = movies["description"].fillna("").astype(str)
movies["rating"] = pd.to_numeric(
    movies["rating"],
    errors="coerce"
).fillna(0.0)


# ============================================================
# LOCAL TF-IDF MODEL
# ============================================================

movies["content"] = (
    movies["genre"] + " " +
    movies["genre"] + " " +
    movies["description"]
)

local_vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

local_tfidf = local_vectorizer.fit_transform(
    movies["content"]
)


# ============================================================
# HELPERS
# ============================================================

def _get_language(item):
    """
    Get the movie's TMDB original language.

    TMDB movie objects normally provide original_language as a
    two-letter ISO 639-1 code such as:
    te = Telugu
    kn = Kannada
    hi = Hindi
    ta = Tamil
    en = English
    """

    return str(
        item.get("original_language")
        or ""
    ).strip().lower()


def _tmdb_text(item):
    """Create searchable content from a TMDB movie dictionary."""

    genres = item.get("genres", [])

    if isinstance(genres, list):
        genre_text = " ".join(
            str(g.get("name", ""))
            for g in genres
            if isinstance(g, dict)
        )
    else:
        genre_text = str(genres or "")

    # Some TMDB endpoints provide genre_ids instead of genre names.
    genre_ids = item.get("genre_ids", [])
    if isinstance(genre_ids, list):
        genre_id_text = " ".join(str(x) for x in genre_ids)
    else:
        genre_id_text = ""

    title = str(
        item.get("title")
        or item.get("original_title")
        or ""
    )

    overview = str(
        item.get("overview")
        or item.get("description")
        or ""
    )

    return (
        f"{title} "
        f"{genre_text} {genre_text} "
        f"{genre_id_text} "
        f"{overview}"
    ).strip()


def _query_text(movie_data):
    """Create the content query for the searched movie."""

    if not movie_data:
        return ""

    return _tmdb_text(movie_data)


# ============================================================
# DYNAMIC CONTENT-BASED RECOMMENDER
# ============================================================

def recommend(
    movie_title,
    movie_data=None,
    candidate_movies=None,
    number_of_movies=5,
):
    """
    Recommend movies specifically for the searched movie.

    Priority:
    1. If TMDB candidate_movies are supplied, use them as the
       movie-specific candidate pool and rank them with TF-IDF.
    2. If the searched movie exists in movies.csv, compare it
       against the local dataset.
    3. Otherwise return [].

    This prevents every searched movie from receiving the same
    five local movies.
    """

    movie_title = str(movie_title or "").strip()

    if not movie_title:
        return []

    # ========================================================
    # PATH A: TMDB CANDIDATES
    # ========================================================

    if movie_data and candidate_movies:

        clean_candidates = []

        searched_id = movie_data.get("id")

        # ----------------------------------------------------
        # SAME-LANGUAGE FILTER
        # ----------------------------------------------------
        # The AI should recommend movies in the same original
        # language as the movie being searched.
        searched_language = _get_language(movie_data)

        for item in candidate_movies:

            if not isinstance(item, dict):
                continue

            candidate_id = item.get("id")

            # Do not recommend the movie itself.
            if searched_id is not None and candidate_id == searched_id:
                continue

            # Reject other-language movies.
            candidate_language = _get_language(item)

            if (
                searched_language
                and candidate_language
                and candidate_language != searched_language
            ):
                continue

            candidate_title = (
                item.get("title")
                or item.get("original_title")
                or ""
            )

            content = _tmdb_text(item)

            if not candidate_title or not content:
                continue

            clean_candidates.append(
                {
                    "item": item,
                    "content": content,
                }
            )

        if clean_candidates:
            query = _query_text(movie_data)

            documents = [query] + [
                x["content"] for x in clean_candidates
            ]

            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2)
            )

            matrix = vectorizer.fit_transform(documents)

            scores = cosine_similarity(
                matrix[0:1],
                matrix[1:]
            ).flatten()

            ranked = sorted(
                zip(clean_candidates, scores),
                key=lambda x: float(x[1]),
                reverse=True
            )

            results = []

            for candidate, score in ranked:

                item = candidate["item"]

                # A tiny rating component helps break ties without
                # overpowering content similarity.
                rating = float(
                    item.get("vote_average") or 0
                )

                final_score = (
                    float(score) * 0.90
                    + (rating / 10.0) * 0.10
                )

                results.append(
                    {
                        "title": (
                            item.get("title")
                            or item.get("original_title")
                            or "Unknown"
                        ),
                        "genre": _genre_names(item),
                        "rating": rating,
                        "similarity": final_score,
                        "tmdb_id": item.get("id"),
                    }
                )

                if len(results) >= number_of_movies:
                    break

            return results

    # ========================================================
    # PATH B: LOCAL CSV MOVIE
    # ========================================================

    title_matches = (
        movies["title"].str.strip().str.lower()
        == movie_title.lower()
    )

    if title_matches.any():

        movie_position = title_matches.to_numpy().nonzero()[0][0]

        scores = cosine_similarity(
            local_tfidf[movie_position],
            local_tfidf
        ).flatten()

        ranked_indices = sorted(
            range(len(movies)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indices:

            if index == movie_position:
                continue

            score = float(scores[index])

            if score <= 0:
                continue

            results.append(
                {
                    "title": movies.iloc[index]["title"],
                    "genre": movies.iloc[index]["genre"],
                    "rating": float(movies.iloc[index]["rating"]),
                    "similarity": score,
                }
            )

            if len(results) >= number_of_movies:
                break

        return results

    return []


def _genre_names(item):
    genres = item.get("genres", [])

    if isinstance(genres, list):
        names = [
            str(g.get("name", ""))
            for g in genres
            if isinstance(g, dict) and g.get("name")
        ]

        if names:
            return ", ".join(names)

    genre = item.get("genre")

    if genre:
        return str(genre)

    return "Movie"


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("                 MOVIE RECOMMENDATION SYSTEM")
    print("=" * 65)

    movie = input("\nEnter a movie name: ").strip()

    recommendations = recommend(
        movie,
        number_of_movies=5
    )

    if not recommendations:

        print("\nMovie not found in the local dataset.")
        print(
            "Use the Streamlit app for TMDB movies such as "
            "KGF, RRR, Salaar, Pushpa, etc."
        )

    else:

        print(f"\nRecommended movies for: {movie}")
        print("-" * 65)

        for item in recommendations:

            print(
                f"{item['title']} | "
                f"Genre: {item['genre']} | "
                f"Rating: {item['rating']:.1f} | "
                f"Similarity: {item['similarity']:.2f}"
            )

        print("-" * 65)
