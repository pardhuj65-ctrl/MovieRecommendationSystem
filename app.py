import streamlit as st
import inspect

from recommendation import recommend

from movie_api import (
    search_movies,
    get_movie_details,
    get_movie_reviews,
    get_similar_movies,
    get_latest_movies,
    get_popular_movies,
    get_trending_movies,
    get_movie_credits,
)

from sentiment import analyze_sentiment


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Movie AI Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def md(content, **kwargs):
    """Render HTML safely after removing Python indentation."""
    if isinstance(content, str):
        content = inspect.cleandoc(content).strip()

        if "<div" in content or "<style" in content or "<span" in content:
            content = "\n".join(
                line for line in content.splitlines() if line.strip()
            )

    kwargs.pop("unsafe_allow_html", None)

    if isinstance(content, str) and (
        "<div" in content or "<style" in content or "<span" in content
    ):
        return st.markdown(content, unsafe_allow_html=True, **kwargs)

    return st.markdown(content, **kwargs)


# ============================================================
# CINEMATIC UI
# ============================================================

md(
    """
<style>
/* ---------- GLOBAL ---------- */
.stApp {
    background: #07111f;
    color: #f5f9ff;
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: rgba(7,17,31,.96);
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: #091827;
    border-right: 1px solid #21415e;
}
section[data-testid="stSidebar"] * {
    color: #eef7ff !important;
}
.sidebar-title {
    font-size: 28px;
    font-weight: 900;
    color: #ffffff !important;
}
.sidebar-subtitle {
    color: #9fdcff !important;
    font-size: 13px;
    margin-bottom: 22px;
}
.language-panel {
    background: #102b45;
    border: 1px solid #2e8fbe;
    border-radius: 12px;
    padding: 13px;
    margin-bottom: 10px;
}
.language-title {
    color: #79ddff !important;
    font-size: 17px;
    font-weight: 900;
}
div[data-baseweb="select"] > div {
    background: #132f4c !important;
    border: 1px solid #4aaed3 !important;
    border-radius: 9px !important;
    min-height: 44px !important;
}
div[data-baseweb="select"] span {
    color: #ffffff !important;
    font-weight: 750 !important;
}
.selected-language {
    margin-top: 9px;
    padding: 9px 12px;
    border-radius: 9px;
    background: #12344d;
    border: 1px solid #2e789b;
    color: #9ee8ff !important;
    font-size: 13px;
    font-weight: 750;
    text-align: center;
}
.feature-title {
    color: #ffd95a !important;
    font-size: 17px;
    font-weight: 900;
}
.feature-item {
    color: #d8eaf7 !important;
    font-size: 14px;
    line-height: 2.05;
}

/* ---------- HERO ---------- */
.hero {
    background: #0d2943;
    border: 1px solid #2d789c;
    border-radius: 18px;
    padding: 30px 24px 25px;
    margin-bottom: 26px;
    box-shadow: 0 12px 35px rgba(0,0,0,.28);
}
.hero-title {
    text-align: center;
    font-size: 42px;
    font-weight: 950;
    color: #ffffff;
    letter-spacing: .5px;
}
.hero-title span {
    color: #62ddff;
}
.hero-subtitle {
    text-align: center;
    color: #d8ebf7;
    font-size: 16px;
    margin-top: 8px;
}
.hero-features {
    display: flex;
    justify-content: space-around;
    gap: 12px;
    margin-top: 24px;
}
.hero-feature {
    text-align: center;
    color: #ffffff;
    font-weight: 800;
    font-size: 14px;
}
.hero-icon {
    display: block;
    font-size: 27px;
    margin-bottom: 5px;
}

/* ---------- HEADINGS ---------- */
.section-title {
    font-size: 28px;
    font-weight: 900;
    color: #ffffff;
    margin-top: 30px;
    margin-bottom: 7px;
}
.section-title.latest {color: #5ee8ff;}
.section-title.trending {color: #ff8edc;}
.section-title.popular {color: #ffd95a;}
.section-description {
    color: #b9cfdf;
    font-size: 14px;
    margin-bottom: 15px;
}

/* ---------- SEARCH ---------- */
.stTextInput > div > div > input {
    background: #0c1d30 !important;
    color: #ffffff !important;
    border: 1px solid #3b88a9 !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    font-size: 16px !important;
}
.stTextInput > div > div > input::placeholder {
    color: #91aabd !important;
}
.stButton > button {
    background: #167db2 !important;
    color: #ffffff !important;
    border: 1px solid #42b9e8 !important;
    border-radius: 10px !important;
    font-weight: 850 !important;
    min-height: 46px !important;
}
.stButton > button:hover {
    background: #2095ce !important;
}

/* ---------- RESULTS / DETAILS ---------- */
.result-row {
    background: #0d2237;
    border: 1px solid #254b66;
    border-radius: 10px;
    padding: 10px 13px;
}
.result-title {
    color: #ffffff;
    font-size: 16px;
    font-weight: 850;
}
.detail-box {
    background: #0d2237;
    border: 1px solid #28526e;
    border-radius: 15px;
    padding: 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,.22);
}
.detail-title {
    font-size: 34px;
    font-weight: 950;
    color: #ffffff;
}
.detail-text {
    color: #dcebf5;
    font-size: 15px;
    line-height: 1.7;
}

/* ---------- CAST ---------- */
.credits-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 12px;
}
.credit-card {
    background: #0d263d;
    border: 1px solid #2d617d;
    border-radius: 13px;
    padding: 17px;
    text-align: center;
}
.credit-icon {
    font-size: 27px;
}
.credit-label {
    color: #8edcf8;
    font-size: 12px;
    font-weight: 850;
    text-transform: uppercase;
}
.credit-name {
    color: #ffffff;
    font-size: 17px;
    font-weight: 900;
    margin-top: 5px;
}
.cast-card {
    background: #0b1d30;
    border: 1px solid #25465c;
    border-radius: 10px;
    padding: 12px;
}
.cast-name {
    color: #ffffff;
    font-weight: 850;
}
.cast-character {
    color: #9fb8c8;
    font-size: 13px;
}

/* ---------- REVIEWS ---------- */
.review-box {
    background: #0c2034;
    border-left: 4px solid #38c8f5;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}
.review-author {
    color: #78dcfa;
    font-weight: 850;
}
.review-text {
    color: #dcebf5;
    line-height: 1.65;
}

/* ---------- AI RECOMMENDATIONS ---------- */
.ai-card {
    background: #172447;
    border: 1px solid #5a63a8;
    border-radius: 13px;
    padding: 16px;
    min-height: 155px;
    box-shadow: 0 8px 22px rgba(0,0,0,.22);
}
.ai-title {
    color: #ffffff;
    font-size: 16px;
    font-weight: 900;
    line-height: 1.4;
}
.ai-score {
    color: #d0b8ff;
    font-size: 14px;
    font-weight: 850;
    margin-top: 11px;
}

/* ---------- MOVIE CARDS ---------- */
.movie-name {
    color: #ffffff;
    font-size: 15px;
    font-weight: 850;
    margin-top: 8px;
    min-height: 40px;
}
.movie-year {
    color: #a9c1d1;
    font-size: 13px;
}
.movie-rating {
    color: #ffd84d;
    font-size: 14px;
    font-weight: 850;
}
.info-box {
    background: #12314a;
    border: 1px solid #327a9e;
    border-radius: 10px;
    padding: 13px;
    color: #d9f2ff;
    font-weight: 650;
}
.cinema-line {
    height: 1px;
    background: #2d6888;
    margin: 28px 0;
}
.footer {
    text-align: center;
    color: #829aaa;
    font-size: 12px;
    padding: 38px 10px;
}

/* ---------- MOBILE ---------- */
@media(max-width:900px) {
    .hero-title {font-size: 30px;}
    .hero-features {flex-direction: column;}
    .credits-grid {grid-template-columns: 1fr;}
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LANGUAGE SETTINGS
# ============================================================

LANGUAGES = {
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Hindi": "hi",
    "English": "en",
}


# ============================================================
# TMDB CACHE
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def cached_search_movies(movie_name):
    return search_movies(movie_name)


@st.cache_data(ttl=600, show_spinner=False)
def cached_movie_details(movie_id):
    return get_movie_details(movie_id)


@st.cache_data(ttl=600, show_spinner=False)
def cached_movie_reviews(movie_id):
    return get_movie_reviews(movie_id)


@st.cache_data(ttl=600, show_spinner=False)
def cached_similar_movies(movie_id):
    return get_similar_movies(movie_id)


@st.cache_data(ttl=600, show_spinner=False)
def cached_movie_credits(movie_id):
    return get_movie_credits(movie_id)


@st.cache_data(ttl=600, show_spinner=False)
def cached_latest_movies(language_code):
    return get_latest_movies(language_code)


@st.cache_data(ttl=600, show_spinner=False)
def cached_popular_movies(language_code):
    return get_popular_movies(language_code)


@st.cache_data(ttl=600, show_spinner=False)
def cached_trending_movies(language_code):
    return get_trending_movies(language_code)


# ============================================================
# SESSION STATE
# ============================================================

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    md('<div class="sidebar-title">🎬 Movie AI</div>')
    md('<div class="sidebar-subtitle">Your Smart Movie Companion</div>')

    md(
        '<div class="language-panel">'
        '<div class="language-title">🌐 Movie Language</div>'
        '</div>'
    )

    selected_language = st.selectbox(
        "🎬 Choose your movie language",
        list(LANGUAGES.keys()),
        index=0,
    )

    language_code = LANGUAGES[selected_language]

    md(
        f"""
        <div class="selected-language">
            🌐 Showing: {selected_language} Movies
        </div>
        """
    )

    md("---")

    md(
        """
        <div class="feature-title">⭐ Features</div>
        <div class="feature-item">
        🔎 Search any movie<br>
        ⭐ Movie ratings<br>
        🎭 Hero, heroine & director<br>
        📝 Real movie reviews<br>
        😊 Sentiment analysis<br>
        🤖 AI content recommendations<br>
        🎯 Smart TMDB recommendations<br>
        🆕 Latest language movies<br>
        🔥 Trending language movies<br>
        ⭐ Popular language movies
        </div>
        """
    )

    md("---")

    md(
        '<div style="color:#9cc8df;font-size:12px;text-align:center;padding-top:15px;">'
        '🎬 Movie information<br>powered by TMDB</div>'
    )


# ============================================================
# HERO
# ============================================================

md(
    """
    <div class="hero">
        <div class="hero-title">🎬 MOVIE <span>AI ASSISTANT</span></div>
        <div class="hero-subtitle">
            Discover movies • Read real reviews • Analyze sentiment •
            Get intelligent recommendations
        </div>
        <div class="hero-features">
            <div class="hero-feature">
                <span class="hero-icon">🔎</span>
                Search<br>Any Movie
            </div>
            <div class="hero-feature">
                <span class="hero-icon">⭐</span>
                Real<br>Reviews
            </div>
            <div class="hero-feature">
                <span class="hero-icon">💗</span>
                Sentiment<br>Analysis
            </div>
            <div class="hero-feature">
                <span class="hero-icon">✨</span>
                Smart<br>Recommendations
            </div>
        </div>
    </div>
    """
)


# ============================================================
# SEARCH
# ============================================================

md('<div class="section-title">🔎 Search Any Movie</div>')
md(
    '<div class="section-description">'
    'Search for any movie from the TMDB database.'
    '</div>'
)

search_col1, search_col2 = st.columns([5, 1])

with search_col1:
    movie_name = st.text_input(
        "Movie name",
        placeholder="Example: KGF, RRR, Salaar, Hanuman...",
        label_visibility="collapsed",
    )

with search_col2:
    search_clicked = st.button(
        "🔎 Search Movie",
        use_container_width=True,
    )


# ============================================================
# SEARCH ACTION
# ============================================================

if search_clicked:
    if not movie_name.strip():
        st.warning("Please enter a movie name.")
    else:
        with st.spinner("🎬 Searching TMDB..."):
            try:
                results = cached_search_movies(movie_name.strip())
            except Exception:
                results = []

        st.session_state.search_results = results[:8]
        st.session_state.selected_movie = None


# ============================================================
# SEARCH RESULTS
# ============================================================

if st.session_state.search_results:
    md('<div class="section-title">🎞️ Search Results</div>')

    for index, movie in enumerate(st.session_state.search_results):
        title = (
            movie.get("title")
            or movie.get("original_title")
            or "Unknown"
        )

        release_date = movie.get("release_date") or "N/A"
        rating = movie.get("vote_average", 0)

        col1, col2, col3, col4 = st.columns([4.5, 1.5, 1, 1.5])

        with col1:
            md(
                f"""
                <div class="result-row">
                    <div class="result-title">🎬 {title}</div>
                </div>
                """
            )

        with col2:
            st.write(f"📅 {release_date}")

        with col3:
            st.write(f"⭐ {rating:.1f}")

        with col4:
            if st.button(
                "View Details",
                key=f"details_{movie.get('id')}_{index}",
                use_container_width=True,
            ):
                with st.spinner("Loading movie..."):
                    details = cached_movie_details(movie.get("id"))

                st.session_state.selected_movie = details
                st.rerun()


# ============================================================
# SELECTED MOVIE
# ============================================================

movie = st.session_state.selected_movie

if movie:
    movie_id = movie.get("id")

    with st.spinner("Loading cast and crew..."):
        try:
            credits = cached_movie_credits(movie_id)
        except Exception:
            credits = {
                "director": "Not Available",
                "hero": "Not Available",
                "heroine": "Not Available",
                "cast": [],
            }

    director = credits.get("director", "Not Available")
    hero = credits.get("hero", "Not Available")
    heroine = credits.get("heroine", "Not Available")
    top_cast = credits.get("cast", [])

    title = movie.get("title") or "Unknown"

    poster_path = movie.get("poster_path")
    poster_url = (
        "https://image.tmdb.org/t/p/w500" + poster_path
        if poster_path
        else None
    )

    rating = movie.get("vote_average", 0)
    release_date = movie.get("release_date") or "N/A"

    original_language = (
        movie.get("original_language") or "N/A"
    ).upper()

    runtime = movie.get("runtime", 0)

    overview = movie.get(
        "overview",
        "No overview available.",
    )

    genres = movie.get("genres", [])

    genre_names = ", ".join(
        g.get("name", "")
        for g in genres
    )

    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    md('<div class="section-title">🎬 Movie Details</div>')

    detail_col1, detail_col2 = st.columns([1, 2])

    with detail_col1:
        if poster_url:
            st.image(
                poster_url,
                use_container_width=True,
            )
        else:
            st.info("Poster not available.")

    with detail_col2:
        md(
            f"""
            <div class="detail-box">
                <div class="detail-title">{title}</div>
                <br>
                <div class="detail-text">
                    ⭐ <b>Rating:</b> {rating:.1f}/10
                    <br><br>
                    📅 <b>Release Date:</b> {release_date}
                    <br><br>
                    🌐 <b>Original Language:</b> {original_language}
                    <br><br>
                    ⏱️ <b>Runtime:</b> {runtime} minutes
                    <br><br>
                    🎭 <b>Genres:</b> {genre_names or "N/A"}
                </div>
            </div>
            """
        )

    # --------------------------------------------------------
    # CAST & CREW
    # --------------------------------------------------------

    md('<div class="section-title">🎭 Cast & Crew</div>')
    md(
        '<div class="section-description">'
        'Main people associated with this movie.'
        '</div>'
    )

    md(
        f"""
        <div class="credits-grid">
            <div class="credit-card">
                <div class="credit-icon">🎬</div>
                <div class="credit-label">Director</div>
                <div class="credit-name">{director}</div>
            </div>
            <div class="credit-card">
                <div class="credit-icon">👨‍🎬</div>
                <div class="credit-label">Hero / Lead Actor</div>
                <div class="credit-name">{hero}</div>
            </div>
            <div class="credit-card">
                <div class="credit-icon">👩‍🎬</div>
                <div class="credit-label">Heroine / Lead Actress</div>
                <div class="credit-name">{heroine}</div>
            </div>
        </div>
        """
    )

    if top_cast:
        md('<div style="height:14px;"></div>')
        md('<div class="section-description"><b>Top Cast</b></div>')

        cast_cols = st.columns(min(5, len(top_cast)))

        for index, person in enumerate(top_cast[:5]):
            with cast_cols[index]:
                profile_path = person.get("profile_path")
                name = person.get("name", "Unknown")
                character = person.get("character", "N/A")

                if profile_path:
                    st.image(
                        "https://image.tmdb.org/t/p/w185" + profile_path,
                        use_container_width=True,
                    )
                else:
                    md(
                        """
                        <div style="
                            height:220px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            background:#08182d;
                            border-radius:12px;
                            color:#789;
                        ">
                            👤 No Image
                        </div>
                        """
                    )

                md(
                    f"""
                    <div class="cast-card">
                        <div class="cast-name">{name}</div>
                        <div class="cast-character">as {character}</div>
                    </div>
                    """
                )

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    md('<div class="section-title">📖 Overview</div>')

    md(
        f"""
        <div class="detail-box">
            <div class="detail-text">{overview}</div>
        </div>
        """
    )

    # --------------------------------------------------------
    # REVIEWS
    # --------------------------------------------------------

    md('<div class="section-title">💬 Movie Reviews</div>')

    with st.spinner("Loading real TMDB reviews..."):
        try:
            reviews = cached_movie_reviews(movie_id)
        except Exception:
            reviews = []

    sentiment_results = []

    if reviews:
        for review in reviews[:10]:
            content = review.get("content", "")
            author = review.get("author", "Anonymous")

            if not content.strip():
                continue

            try:
                sentiment = analyze_sentiment(content)
            except Exception:
                sentiment = "Neutral 😐"

            sentiment_results.append(sentiment)

            md(
                f"""
                <div class="review-box">
                    <div class="review-author">👤 {author}</div>
                    <br>
                    <div class="review-text">{content}</div>
                    <br>
                    <b>Sentiment:</b> {sentiment}
                </div>
                """
            )

    else:
        md(
            '<div class="info-box">'
            '💬 No TMDB reviews are available for this movie right now.'
            '</div>'
        )

    # --------------------------------------------------------
    # SENTIMENT ANALYSIS
    # --------------------------------------------------------

    if sentiment_results:
        positive = sum(
            1 for x in sentiment_results
            if "Positive" in x
        )

        negative = sum(
            1 for x in sentiment_results
            if "Negative" in x
        )

        neutral = sum(
            1 for x in sentiment_results
            if "Neutral" in x
        )

        total = len(sentiment_results)

        md(
            '<div class="section-title">😊 Sentiment Analysis</div>'
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Positive",
                f"{positive / total * 100:.0f}%",
            )

        with c2:
            st.metric(
                "Neutral",
                f"{neutral / total * 100:.0f}%",
            )

        with c3:
            st.metric(
                "Negative",
                f"{negative / total * 100:.0f}%",
            )

    # --------------------------------------------------------
    # TMDB RECOMMENDATIONS
    # --------------------------------------------------------

    md(
        '<div class="section-title">🎯 Recommended Movies</div>'
    )

    md(
        """
        <div class="section-description">
            TMDB recommendations based on the selected movie
            and its available movie relationships.
        </div>
        """
    )

    with st.spinner("Finding similar movies..."):
        try:
            recommendations = cached_similar_movies(movie_id)
        except Exception:
            recommendations = []

    if recommendations:
        cols = st.columns(min(5, len(recommendations)))

        for index, rec in enumerate(recommendations[:5]):
            with cols[index]:
                rec_poster = rec.get("poster_path")

                if rec_poster:
                    st.image(
                        "https://image.tmdb.org/t/p/w500" + rec_poster,
                        use_container_width=True,
                    )

                rec_title = rec.get("title") or "Unknown"

                rec_rating = rec.get(
                    "vote_average",
                    0,
                )

                rec_year = (
                    rec.get("release_date") or "N/A"
                )[:4]

                md(
                    f"""
                    <div class="movie-name">{rec_title}</div>
                    <div class="movie-year">{rec_year}</div>
                    <div class="movie-rating">⭐ {rec_rating:.1f}</div>
                    """
                )

    else:
        md(
            '<div class="info-box">'
            '🎯 No TMDB recommendations were found for this movie.'
            '</div>'
        )

    # --------------------------------------------------------
    # AI CONTENT-BASED RECOMMENDATIONS
    # --------------------------------------------------------

    md(
        '<div class="section-title ai">🤖 AI Content-Based Recommendations</div>'
    )

    md(
        """
        <div class="section-description">
            Recommendations generated using <b>TF-IDF + Cosine Similarity</b>
            from your local <b>movies.csv</b> dataset.
            The AI compares movie <b>genre + description</b>.
        </div>
        """
    )

    try:
        # Use the selected TMDB movie as the AI query.
        # First use movie-specific TMDB recommendations/similar movies.
        # If that list is too small for a particular movie (such as
        # Jersey), add movies from the SAME original language.
        # TF-IDF + Cosine Similarity then ranks the combined pool.
        tmdb_candidates = cached_similar_movies(movie_id) or []

        searched_language = str(
            movie.get("original_language") or ""
        ).strip().lower()

        if searched_language:
            try:
                language_movies = cached_popular_movies(searched_language) or []
            except Exception:
                language_movies = []

            existing_ids = {
                item.get("id")
                for item in tmdb_candidates
                if isinstance(item, dict) and item.get("id") is not None
            }

            for item in language_movies:
                if not isinstance(item, dict):
                    continue
                item_id = item.get("id")
                if item_id is not None and item_id not in existing_ids:
                    tmdb_candidates.append(item)
                    existing_ids.add(item_id)

        ai_recommendations = recommend(
            title,
            movie_data=movie,
            candidate_movies=tmdb_candidates,
            number_of_movies=5,
        )
    except Exception:
        ai_recommendations = []

    if ai_recommendations:

        ai_cols = st.columns(min(5, len(ai_recommendations)))

        for index, item in enumerate(ai_recommendations):

            with ai_cols[index]:

                ai_title = item.get("title", "Unknown")
                ai_genre = item.get("genre", "N/A")
                ai_rating = item.get("rating", 0)
                similarity_score = item.get("similarity", 0)

                # Convert similarity into a percentage for easier reading.
                similarity_percent = similarity_score * 100

                md(
                    f"""
                    <div class="ai-card">
                        <div class="ai-title">
                            🤖 {ai_title}
                        </div>

                        <div style="
                            color:#9fdfff;
                            font-size:12px;
                            margin-top:8px;
                            line-height:1.5;
                        ">
                            🎭 {ai_genre}
                        </div>

                        <div style="
                            color:#ffd52f;
                            font-size:13px;
                            font-weight:800;
                            margin-top:8px;
                        ">
                            ⭐ Rating: {ai_rating:.1f}/10
                        </div>

                        <div class="ai-score">
                            🧠 Similarity: {similarity_percent:.0f}%
                        </div>
                    </div>
                    """
                )

        md(
            """
            <div class="info-box" style="margin-top:15px;">
                🧠 <b>How it works:</b>
                TF-IDF converts the movie genre and description into
                numerical features, then Cosine Similarity compares them
                with the selected movie to find the most similar titles.
            </div>
            """
        )

    else:

        md(
            '<div class="info-box">'
            '🤖 No strong content-based matches were found. '
            'Try another movie with a more detailed description.'
            '</div>'
        )


# ============================================================
# SEPARATOR
# ============================================================

md('<div class="cinema-line"></div>')


# ============================================================
# MOVIE ROW HELPER
# ============================================================

def display_movie_row(movies):
    if not movies:
        md(
            '<div class="info-box">'
            '🎬 No movies are available for this section right now. Check your TMDB connection or try another language.'
            '</div>'
        )
        return

    movies = movies[:6]

    columns = st.columns(len(movies))

    for index, movie_item in enumerate(movies):
        with columns[index]:
            poster_path = movie_item.get("poster_path")

            if poster_path:
                st.image(
                    "https://image.tmdb.org/t/p/w500" + poster_path,
                    use_container_width=True,
                )
            else:
                md(
                    """
                    <div style="
                        height:260px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        background:#08182d;
                        border-radius:12px;
                        color:#789;
                    ">
                        🎬 No Poster
                    </div>
                    """
                )

            movie_title = (
                movie_item.get("title")
                or movie_item.get("original_title")
                or "Unknown"
            )

            year = movie_item.get("release_date") or "N/A"

            year = (
                year[:4]
                if year != "N/A"
                else year
            )

            movie_rating = movie_item.get(
                "vote_average",
                0,
            )

            md(
                f"""
                <div class="movie-name">{movie_title}</div>
                <div class="movie-year">{year}</div>
                <div class="movie-rating">⭐ {movie_rating:.1f}</div>
                """
            )


# ============================================================
# LATEST MOVIES
# ============================================================

with st.spinner(
    f"Loading latest {selected_language} movies..."
):
    try:
        latest_movies = cached_latest_movies(language_code)
    except Exception:
        latest_movies = []

md(
    f"""
    <div class="section-title latest">
        🆕 Latest {selected_language} Movies
    </div>

    <div class="section-description">
        Recently released {selected_language} movies
    </div>
    """
)

display_movie_row(latest_movies)


# ============================================================
# TRENDING MOVIES
# ============================================================

with st.spinner(
    f"Loading trending {selected_language} movies..."
):
    try:
        trending_movies = cached_trending_movies(language_code)
    except Exception:
        trending_movies = []

if not trending_movies:
    try:
        trending_movies = cached_popular_movies(language_code)
    except Exception:
        trending_movies = []

md(
    f"""
    <div class="section-title trending">
        🔥 Trending {selected_language} Movies
    </div>

    <div class="section-description">
        Currently popular {selected_language} movies
    </div>
    """
)

display_movie_row(trending_movies)


# ============================================================
# POPULAR MOVIES
# ============================================================

with st.spinner(
    f"Loading popular {selected_language} movies..."
):
    try:
        popular_movies = cached_popular_movies(language_code)
    except Exception:
        popular_movies = []

md(
    f"""
    <div class="section-title popular">
        ⭐ Popular {selected_language} Movies
    </div>

    <div class="section-description">
        Most popular {selected_language} movies on TMDB
    </div>
    """
)

display_movie_row(popular_movies)


# ============================================================
# FOOTER
# ============================================================

md(
    """
    <div class="footer">
        🎬 <b>Movie AI Assistant</b>
        <br><br>
        Search • Reviews • Sentiment • AI Recommendations •
        Latest • Trending • Popular
        <br><br>
        Movie information powered by TMDB
    </div>
    """
)

