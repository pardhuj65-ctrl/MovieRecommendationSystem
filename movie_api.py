import os
from datetime import date, timedelta

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"


# ============================================================
# COMMON TMDB REQUEST
# ============================================================

def tmdb_get(endpoint, params=None):

    if not API_KEY:
        print("ERROR: TMDB_API_KEY not found in .env")
        return None

    if params is None:
        params = {}

    params["api_key"] = API_KEY

    try:

        response = requests.get(
            f"{BASE_URL}{endpoint}",
            params=params,
            timeout=20
        )

        if response.status_code != 200:

            print(
                "TMDB ERROR:",
                response.status_code
            )

            return None

        return response.json()

    except requests.exceptions.RequestException as e:

        print("TMDB CONNECTION ERROR:", e)

        return None


# ============================================================
# SEARCH MOVIES
# ============================================================

def search_movies(movie_name):

    params = {
        "query": movie_name,
        "language": "en-US",
        "include_adult": False,
        "page": 1
    }

    data = tmdb_get(
        "/search/movie",
        params
    )

    if not data:
        return []

    return data.get(
        "results",
        []
    )


# ============================================================
# MOVIE DETAILS
# ============================================================

def get_movie_details(movie_id):

    params = {
        "language": "en-US"
    }

    return tmdb_get(
        f"/movie/{movie_id}",
        params
    )


# ============================================================
# MOVIE REVIEWS
# ============================================================

def get_movie_reviews(movie_id):

    params = {
        "language": "en-US",
        "page": 1
    }

    data = tmdb_get(
        f"/movie/{movie_id}/reviews",
        params
    )

    if not data:
        return []

    return data.get(
        "results",
        []
    )


# ============================================================
# SIMILAR MOVIES
# ============================================================

def get_similar_movies(movie_id):

    movie = get_movie_details(movie_id)

    if not movie:
        return []

    original_language = movie.get(
        "original_language",
        ""
    )

    data = tmdb_get(
        f"/movie/{movie_id}/similar",
        {
            "language": "en-US",
            "page": 1
        }
    )

    if not data:
        return []

    movies = data.get(
        "results",
        []
    )

    same_language = []

    for item in movies:

        if item.get(
            "original_language"
        ) == original_language:

            same_language.append(item)

    return same_language[:10]


# ============================================================
# DISCOVER LANGUAGE MOVIES
# ============================================================

def discover_language_movies(
    language_code,
    sort_by="popularity.desc",
    min_date=None,
    max_date=None,
    pages=3
):

    all_movies = []

    for page in range(1, pages + 1):

        params = {

            "language": "en-US",

            "sort_by": sort_by,

            "with_original_language":
                language_code,

            "page": page,

            "include_adult": False,

            "vote_count.gte": 1
        }

        if min_date:

            params[
                "primary_release_date.gte"
            ] = min_date

        if max_date:

            params[
                "primary_release_date.lte"
            ] = max_date

        data = tmdb_get(
            "/discover/movie",
            params
        )

        if not data:
            continue

        results = data.get(
            "results",
            []
        )

        for movie in results:

            # Extra language safety check
            if movie.get(
                "original_language"
            ) == language_code:

                if movie not in all_movies:

                    all_movies.append(movie)

    return all_movies


# ============================================================
# LATEST LANGUAGE MOVIES
# ============================================================

def get_latest_movies(language_code):

    today = date.today()

    # --------------------------------------------------------
    # TRY 1: Last 6 months
    # --------------------------------------------------------

    start_date = (
        today - timedelta(days=180)
    ).isoformat()

    movies = discover_language_movies(

        language_code,

        sort_by="primary_release_date.desc",

        min_date=start_date,

        max_date=today.isoformat(),

        pages=3
    )

    if len(movies) >= 5:

        return movies[:10]


    # --------------------------------------------------------
    # TRY 2: Last 1 year
    # --------------------------------------------------------

    start_date = (
        today - timedelta(days=365)
    ).isoformat()

    movies = discover_language_movies(

        language_code,

        sort_by="primary_release_date.desc",

        min_date=start_date,

        max_date=today.isoformat(),

        pages=4
    )

    if len(movies) >= 5:

        return movies[:10]


    # --------------------------------------------------------
    # TRY 3: Last 2 years
    # --------------------------------------------------------

    start_date = (
        today - timedelta(days=730)
    ).isoformat()

    movies = discover_language_movies(

        language_code,

        sort_by="primary_release_date.desc",

        min_date=start_date,

        max_date=today.isoformat(),

        pages=5
    )

    if movies:

        return movies[:10]


    # --------------------------------------------------------
    # FINAL FALLBACK
    # --------------------------------------------------------

    movies = discover_language_movies(

        language_code,

        sort_by="popularity.desc",

        pages=5
    )

    return movies[:10]


# ============================================================
# POPULAR LANGUAGE MOVIES
# ============================================================

def get_popular_movies(language_code):

    movies = discover_language_movies(

        language_code,

        sort_by="popularity.desc",

        pages=5
    )

    return movies[:10]


# ============================================================
# TRENDING LANGUAGE MOVIES
# ============================================================

def get_trending_movies(language_code):

    # --------------------------------------------------------
    # FIRST: TMDB GLOBAL TRENDING
    # --------------------------------------------------------

    all_trending = []

    for page in range(1, 4):

        data = tmdb_get(
            "/trending/movie/week",
            {
                "language": "en-US",
                "page": page
            }
        )

        if not data:
            continue

        results = data.get(
            "results",
            []
        )

        for movie in results:

            if movie.get(
                "original_language"
            ) == language_code:

                if movie not in all_trending:

                    all_trending.append(movie)

    if len(all_trending) >= 5:

        return all_trending[:10]


    # --------------------------------------------------------
    # FALLBACK 1: POPULAR + RECENT
    # --------------------------------------------------------

    recent_start = (
        date.today() -
        timedelta(days=365)
    ).isoformat()

    recent_movies = discover_language_movies(

        language_code,

        sort_by="popularity.desc",

        min_date=recent_start,

        max_date=date.today().isoformat(),

        pages=5
    )

    if recent_movies:

        return recent_movies[:10]


    # --------------------------------------------------------
    # FALLBACK 2: ALL POPULAR LANGUAGE MOVIES
    # --------------------------------------------------------

    popular_movies = discover_language_movies(

        language_code,

        sort_by="popularity.desc",

        pages=5
    )

    return popular_movies[:10]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("       TMDB LANGUAGE TEST")
    print("======================================")

    languages = {

        "Telugu": "te",

        "Tamil": "ta",

        "Kannada": "kn",

        "Malayalam": "ml",

        "Hindi": "hi",

        "English": "en"
    }

    for name, code in languages.items():

        print()
        print(
            f"Testing {name}..."
        )

        latest = get_latest_movies(code)

        popular = get_popular_movies(code)

        trending = get_trending_movies(code)

        print(
            "Latest:",
            len(latest)
        )

        print(
            "Popular:",
            len(popular)
        )

        print(
            "Trending:",
            len(trending)
        )

        if popular:

            print(
                "Example:",
                popular[0].get("title")
            )

    print()
    print("======================================")
    print("              DONE")
    print("======================================")