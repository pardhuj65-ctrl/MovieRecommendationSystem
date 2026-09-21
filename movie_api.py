import os
from datetime import date

import requests
from dotenv import load_dotenv


# =========================================================
# TMDB CONFIGURATION
# =========================================================

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

REQUEST_TIMEOUT = 10

SESSION = requests.Session()


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

LANGUAGES = {
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Hindi": "hi",
    "English": "en",
}


# =========================================================
# COMMON TMDB REQUEST FUNCTION
# =========================================================

def _request(endpoint, params=None):
    """
    Safely send a request to TMDB.
    """

    if not API_KEY:
        print("ERROR: TMDB_API_KEY not found.")
        return {}

    url = f"{BASE_URL}{endpoint}"

    request_params = {
        "api_key": API_KEY
    }

    if params:
        request_params.update(params)

    try:

        response = SESSION.get(
            url,
            params=request_params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:

        print(f"TMDB timeout: {endpoint}")

        return {}

    except requests.exceptions.RequestException as error:

        print(f"TMDB request error: {error}")

        return {}

    except ValueError:

        print("TMDB returned invalid JSON.")

        return {}


# =========================================================
# CLEAN MOVIE RESULTS
# =========================================================

def _clean_movies(movies):

    cleaned = []

    seen_ids = set()

    for movie in movies or []:

        movie_id = movie.get("id")

        if not movie_id:
            continue

        if movie_id in seen_ids:
            continue

        title = (
            movie.get("title")
            or movie.get("original_title")
            or ""
        ).strip()

        if not title:
            continue

        seen_ids.add(movie_id)

        cleaned.append(movie)

    return cleaned


# =========================================================
# LANGUAGE FILTER
# =========================================================

def _filter_language(movies, language_code):

    return [
        movie
        for movie in _clean_movies(movies)
        if movie.get("original_language") == language_code
    ]


# =========================================================
# SEARCH MOVIES
# =========================================================

def search_movies(movie_name):
    """
    Search TMDB.

    Exact title matches are prioritized first.
    Popular and relevant results follow.
    """

    if not movie_name or not movie_name.strip():
        return []

    query = movie_name.strip()

    data = _request(
        "/search/movie",
        {
            "query": query,
            "language": "en-US",
            "include_adult": False,
            "page": 1
        }
    )

    results = _clean_movies(
        data.get("results", [])
    )

    query_lower = query.casefold()

    def score_movie(movie):

        title = (
            movie.get("title")
            or movie.get("original_title")
            or ""
        ).casefold()

        original_title = (
            movie.get("original_title")
            or ""
        ).casefold()

        # Exact title
        if title == query_lower:

            match_score = 1000000

        # Exact original title
        elif original_title == query_lower:

            match_score = 900000

        # Title starts with search
        elif title.startswith(query_lower):

            match_score = 500000

        # Search term occurs in title
        elif query_lower in title:

            match_score = 250000

        else:

            match_score = 0

        popularity = movie.get(
            "popularity",
            0
        ) or 0

        vote_count = movie.get(
            "vote_count",
            0
        ) or 0

        return (
            match_score,
            popularity,
            vote_count
        )

    results.sort(
        key=score_movie,
        reverse=True
    )

    return results[:10]


# =========================================================
# MOVIE DETAILS
# =========================================================

def get_movie_details(movie_id):
    """
    Get complete movie information.
    """

    if not movie_id:
        return {}

    return _request(
        f"/movie/{movie_id}",
        {
            "language": "en-US"
        }
    )


# =========================================================
# MOVIE REVIEWS
# =========================================================

def get_movie_reviews(movie_id):
    """
    Get real reviews from TMDB.

    First tries English reviews.
    If none are available, tries the general review endpoint.
    """

    if not movie_id:
        return []

    # First request
    data = _request(
        f"/movie/{movie_id}/reviews",
        {
            "language": "en-US",
            "page": 1
        }
    )

    reviews = data.get(
        "results",
        []
    ) or []

    if reviews:
        return reviews

    # Fallback request
    fallback = _request(
        f"/movie/{movie_id}/reviews",
        {
            "page": 1
        }
    )

    return fallback.get(
        "results",
        []
    ) or []


# =========================================================
# RECOMMENDED MOVIES
# =========================================================

def get_similar_movies(movie_id):
    """
    Get intelligent TMDB recommendations.

    Priority:

    1. TMDB recommendations
    2. Same-language recommendations
    3. Similar movies fallback
    """

    if not movie_id:
        return []

    # -----------------------------------------------------
    # Get selected movie language
    # -----------------------------------------------------

    movie_details = get_movie_details(movie_id)

    selected_language = movie_details.get(
        "original_language"
    )

    # -----------------------------------------------------
    # TMDB Recommendations
    # -----------------------------------------------------

    recommendation_data = _request(
        f"/movie/{movie_id}/recommendations",
        {
            "language": "en-US",
            "page": 1
        }
    )

    recommendations = _clean_movies(
        recommendation_data.get(
            "results",
            []
        )
    )

    # -----------------------------------------------------
    # Prefer same-language movies
    # -----------------------------------------------------

    if selected_language:

        same_language = _filter_language(
            recommendations,
            selected_language
        )

        if same_language:

            recommendations = same_language

    # -----------------------------------------------------
    # Similar Movies Fallback
    # -----------------------------------------------------

    if len(recommendations) < 5:

        similar_data = _request(
            f"/movie/{movie_id}/similar",
            {
                "language": "en-US",
                "page": 1
            }
        )

        similar_movies = _clean_movies(
            similar_data.get(
                "results",
                []
            )
        )

        if selected_language:

            same_language_similar = _filter_language(
                similar_movies,
                selected_language
            )

            if same_language_similar:

                similar_movies = same_language_similar

        existing_ids = {
            movie.get("id")
            for movie in recommendations
        }

        for movie in similar_movies:

            movie_id_value = movie.get("id")

            if movie_id_value not in existing_ids:

                recommendations.append(movie)

                existing_ids.add(
                    movie_id_value
                )

    recommendations = _clean_movies(
        recommendations
    )

    return recommendations[:10]


# =========================================================
# DISCOVER MOVIES BY LANGUAGE
# =========================================================

def _discover_movies(
    language_code,
    sort_by="popularity.desc",
    extra_params=None
):
    """
    Use TMDB Discover.

    This gives much better language-specific results than
    using the general popular endpoint.
    """

    if not language_code:
        return []

    params = {

        "language": "en-US",

        "with_original_language": language_code,

        "sort_by": sort_by,

        "include_adult": False,

        "include_video": False,

        "page": 1
    }

    if extra_params:

        params.update(
            extra_params
        )

    data = _request(
        "/discover/movie",
        params
    )

    return _clean_movies(
        data.get(
            "results",
            []
        )
    )


# =========================================================
# LATEST MOVIES
# =========================================================

def get_latest_movies(language_code):
    """
    Get the latest released movies for the selected language.

    Uses multiple TMDB Discover pages and sorts the results
    locally by release date so the section does not become
    empty because of overly strict TMDB filters.
    """

    if not language_code:
        return []

    today = date.today().isoformat()

    all_movies = []

    # Fetch several pages to get a larger pool of movies.
    for page in range(1, 4):

        data = _request(
            "/discover/movie",
            {
                "language": "en-US",
                "with_original_language": language_code,
                "include_adult": False,
                "include_video": False,
                "sort_by": "primary_release_date.desc",
                "page": page
            }
        )

        movies = data.get(
            "results",
            []
        ) or []

        all_movies.extend(movies)

    # Remove duplicates.
    all_movies = _clean_movies(all_movies)

    # Keep only movies having a valid release date.
    valid_movies = []

    for movie in all_movies:

        release_date = movie.get(
            "release_date"
        )

        if not release_date:
            continue

        # Ignore future releases.
        if release_date > today:
            continue

        # Make sure the movie really belongs
        # to the selected language.
        if movie.get(
            "original_language"
        ) != language_code:
            continue

        valid_movies.append(movie)

    # Sort newest first.
    valid_movies.sort(
        key=lambda movie: movie.get(
            "release_date",
            ""
        ),
        reverse=True
    )

    return valid_movies[:6]
def get_popular_movies(language_code):
    """
    Get established popular movies
    for the selected language.
    """

    movies = _discover_movies(

        language_code,

        sort_by="popularity.desc",

        extra_params={

            "vote_count.gte": 20
        }
    )

    return movies[:12]


# =========================================================
# TRENDING MOVIES
# =========================================================

def get_trending_movies(language_code):
    """
    Get currently trending movies.

    TMDB's trending endpoint cannot directly filter by
    original language, so we fetch trending movies and
    filter them locally.

    If there are not enough movies, language-specific
    popular movies are used as a fallback.
    """

    if not language_code:
        return []

    trending_data = _request(
        "/trending/movie/week",
        {
            "language": "en-US"
        }
    )

    trending_movies = trending_data.get(
        "results",
        []
    ) or []

    # Filter selected language
    trending_movies = _filter_language(
        trending_movies,
        language_code
    )

    trending_movies = _clean_movies(
        trending_movies
    )

    # -----------------------------------------------------
    # Fallback if there are not enough trending movies
    # -----------------------------------------------------

    if len(trending_movies) < 6:

        fallback = _discover_movies(

            language_code,

            sort_by="popularity.desc",

            extra_params={
                "vote_count.gte": 5
            }
        )

        existing_ids = {
            movie.get("id")
            for movie in trending_movies
        }

        for movie in fallback:

            movie_id_value = movie.get(
                "id"
            )

            if movie_id_value not in existing_ids:

                trending_movies.append(
                    movie
                )

                existing_ids.add(
                    movie_id_value
                )

    return trending_movies[:12]


# =========================================================
# POSTER URL HELPER
# =========================================================

def get_poster_url(poster_path):
    """
    Convert TMDB poster_path into a complete image URL.
    """

    if not poster_path:
        return None

    return (
        f"{IMAGE_BASE_URL}"
        f"{poster_path}"
    )
# =========================================================
# MOVIE CREDITS
# =========================================================

def get_movie_credits(movie_id):
    """
    Get director, hero, heroine and top cast
    information from TMDB.
    """

    if not movie_id:
        return {
            "director": "Not Available",
            "hero": "Not Available",
            "heroine": "Not Available",
            "cast": [],
        }

    # Get credits from TMDB
    endpoint = f"/movie/{movie_id}/credits"

    # IMPORTANT:
    # Use _request(), because this is the TMDB
    # request function defined at the top of this file.
    data = _request(
        endpoint,
        {
            "language": "en-US"
        }
    )

    if not data:
        return {
            "director": "Not Available",
            "hero": "Not Available",
            "heroine": "Not Available",
            "cast": [],
        }

    crew = data.get("crew", []) or []
    cast = data.get("cast", []) or []

    # =====================================================
    # DIRECTOR
    # =====================================================

    director = "Not Available"

    for person in crew:

        if person.get("job") == "Director":

            director = person.get(
                "name",
                "Not Available"
            )

            break

    # =====================================================
    # TOP CAST
    # =====================================================

    top_cast = []

    for person in cast[:10]:

        top_cast.append(
            {
                "name": person.get(
                    "name",
                    "Unknown"
                ),

                "character": person.get(
                    "character",
                    ""
                ),

                "profile_path": person.get(
                    "profile_path"
                ),
            }
        )

    # =====================================================
    # HERO
    # =====================================================

    hero = "Not Available"

    for person in cast:

        # TMDB gender:
        # 1 = Female
        # 2 = Male

        if person.get("gender") == 2:

            hero = person.get(
                "name",
                "Not Available"
            )

            break

    # Fallback
    if hero == "Not Available" and cast:

        hero = cast[0].get(
            "name",
            "Not Available"
        )

    # =====================================================
    # HEROINE
    # =====================================================

    heroine = "Not Available"

    for person in cast:

        if person.get("gender") == 1:

            heroine = person.get(
                "name",
                "Not Available"
            )

            break

    # =====================================================
    # RETURN ALL INFORMATION
    # =====================================================

    return {
        "director": director,
        "hero": hero,
        "heroine": heroine,
        "cast": top_cast,
    }