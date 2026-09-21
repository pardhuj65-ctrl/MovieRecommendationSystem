import streamlit as st
import inspect

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
.stApp {
    background:
        radial-gradient(circle at 75% 5%, rgba(65,90,255,.20), transparent 30%),
        radial-gradient(circle at 20% 55%, rgba(0,180,255,.12), transparent 35%),
        radial-gradient(circle at 90% 80%, rgba(170,40,255,.10), transparent 30%),
        linear-gradient(135deg,#020611 0%,#061329 45%,#030713 100%);
    color:#fff;
}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}

section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#020713 0%,#06172c 45%,#020817 100%);
    border-right:1px solid rgba(55,190,255,.28);
    box-shadow:8px 0 40px rgba(0,80,180,.12);
}
section[data-testid="stSidebar"] * {color:#eaf7ff !important;}

.sidebar-title {
    font-size:27px;
    font-weight:900;
    color:#fff;
    text-shadow:0 0 8px rgba(60,190,255,.75),0 0 20px rgba(80,100,255,.45);
}
.sidebar-subtitle {
    color:#8edfff;
    font-size:12px;
    font-weight:600;
    margin-bottom:25px;
}

.language-panel {
    background:linear-gradient(135deg,rgba(15,55,100,.95),rgba(20,25,70,.95));
    border:1px solid rgba(50,190,255,.55);
    border-radius:16px;
    padding:15px;
    margin-bottom:10px;
    box-shadow:0 0 22px rgba(0,160,255,.12);
}
.language-title {
    color:#8de9ff !important;
    font-size:17px;
    font-weight:900;
}

div[data-baseweb="select"] > div {
    background:linear-gradient(135deg,#162e56,#173a69) !important;
    border:1px solid rgba(90,220,255,.65) !important;
    border-radius:11px !important;
    min-height:44px !important;
    box-shadow:0 0 15px rgba(0,180,255,.12);
}
div[data-baseweb="select"] span {
    color:#fff !important;
    font-weight:750 !important;
}

.selected-language {
    margin-top:10px;
    padding:10px 14px;
    border-radius:10px;
    background:rgba(30,120,180,0.18);
    border:1px solid rgba(70,200,255,0.35);
    color:#8eeaff !important;
    font-size:13px;
    font-weight:700;
    text-align:center;
}

.feature-title {
    color:#ffd84d !important;
    font-size:17px;
    font-weight:900;
    margin-bottom:15px;
}
.feature-item {
    color:#d9efff !important;
    font-size:14px;
    font-weight:650;
    line-height:2.35;
}

.hero {
    background:
        radial-gradient(circle at 10% 30%,rgba(20,130,255,.35),transparent 35%),
        radial-gradient(circle at 90% 60%,rgba(200,40,255,.22),transparent 35%),
        linear-gradient(135deg,rgba(7,37,85,.98),rgba(14,20,65,.98),rgba(35,10,65,.98));
    border:1px solid rgba(70,190,255,.55);
    border-radius:22px;
    padding:35px 25px 30px;
    margin-bottom:30px;
    box-shadow:0 15px 55px rgba(0,0,0,.45),inset 0 0 50px rgba(40,130,255,.08);
}
.hero-title {
    text-align:center;
    font-size:43px;
    font-weight:950;
    color:#fff;
    letter-spacing:1px;
    text-shadow:0 0 8px rgba(100,220,255,.85),0 0 25px rgba(80,120,255,.50);
}
.hero-title span {
    background:linear-gradient(90deg,#fff,#7eeaff,#c98cff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-subtitle {
    text-align:center;
    color:#e7f6ff;
    font-size:16px;
    font-weight:650;
    margin-top:7px;
}
.hero-features {
    display:flex;
    justify-content:space-around;
    margin-top:28px;
    gap:10px;
}
.hero-feature {
    text-align:center;
    color:#eaf8ff;
    font-weight:800;
    font-size:14px;
}
.hero-icon {
    font-size:28px;
    display:block;
    margin-bottom:5px;
}

.section-title {
    font-size:28px;
    font-weight:900;
    color:#fff;
    margin-top:30px;
    margin-bottom:7px;
    text-shadow:0 0 12px rgba(70,190,255,.35);
}
.section-title.latest {color:#28dcff;}
.section-title.trending {color:#ff72d7;}
.section-title.popular {color:#ffd34f;}
.section-description {
    color:#b8d8ef;
    font-size:14px;
    margin-bottom:15px;
}

.stTextInput > div > div > input {
    background:rgba(8,20,40,.95) !important;
    color:#fff !important;
    border:1px solid rgba(70,190,255,.55) !important;
    border-radius:11px !important;
    font-size:16px !important;
    min-height:45px !important;
}
.stTextInput > div > div > input::placeholder {
    color:#8faac0 !important;
}

.stButton > button {
    background:linear-gradient(90deg,#11bde5,#466eff,#9b35ff) !important;
    color:#fff !important;
    border:none !important;
    border-radius:11px !important;
    font-weight:850 !important;
    min-height:43px !important;
    box-shadow:0 5px 18px rgba(50,150,255,.20);
}
.stButton > button:hover {
    box-shadow:0 0 25px rgba(60,190,255,.45) !important;
}

.result-row {
    background:rgba(10,27,48,.82);
    border:1px solid rgba(70,170,230,.22);
    border-radius:12px;
    padding:10px 14px;
    margin-bottom:8px;
}
.result-title {
    color:#fff;
    font-size:16px;
    font-weight:850;
}

.movie-name {
    color:#fff;
    font-size:15px;
    font-weight:850;
    margin-top:8px;
    min-height:40px;
}
.movie-year {
    color:#9dbbd3;
    font-size:13px;
}
.movie-rating {
    color:#ffd52f;
    font-size:14px;
    font-weight:850;
}

.detail-box {
    background:linear-gradient(135deg,rgba(15,35,62,.97),rgba(5,15,29,.98));
    border:1px solid rgba(70,190,255,.30);
    border-radius:17px;
    padding:23px;
    box-shadow:0 12px 35px rgba(0,0,0,.30);
}
.detail-title {
    font-size:35px;
    font-weight:950;
    color:#fff;
    text-shadow:0 0 10px rgba(70,200,255,.30);
}
.detail-text {
    color:#d9ecfa;
    font-size:15px;
    line-height:1.7;
}

.credits-grid {
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:14px;
    margin-top:12px;
}
.credit-card {
    background:linear-gradient(135deg,rgba(12,42,72,.96),rgba(8,19,39,.98));
    border:1px solid rgba(80,205,255,.30);
    border-radius:15px;
    padding:18px;
    text-align:center;
    box-shadow:0 8px 25px rgba(0,0,0,.22);
}
.credit-icon {
    font-size:28px;
    margin-bottom:7px;
}
.credit-label {
    color:#91ddf8;
    font-size:12px;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:.8px;
}
.credit-name {
    color:#fff;
    font-size:18px;
    font-weight:900;
    margin-top:5px;
}
.cast-card {
    background:rgba(9,25,44,.88);
    border:1px solid rgba(80,190,235,.20);
    border-radius:12px;
    padding:13px;
    margin-bottom:8px;
}
.cast-name {
    color:#fff;
    font-weight:850;
}
.cast-character {
    color:#9fc6da;
    font-size:13px;
    margin-top:3px;
}

.review-box {
    background:linear-gradient(135deg,rgba(13,32,53,.95),rgba(5,14,27,.98));
    border-left:4px solid #36cfff;
    border-radius:12px;
    padding:17px;
    margin-bottom:13px;
}
.review-author {
    color:#77dfff;
    font-weight:850;
}
.review-text {
    color:#dcecf8;
    line-height:1.65;
}

.info-box {
    background:linear-gradient(90deg,rgba(15,60,100,.80),rgba(40,35,100,.70));
    border:1px solid rgba(50,190,255,.25);
    border-radius:11px;
    padding:13px;
    color:#a9eaff;
    font-weight:650;
}

.movie-card-box {
    min-height:390px;
}

.cinema-line {
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(60,190,255,.65),rgba(180,70,255,.55),transparent);
    margin:25px 0;
}

.footer {
    text-align:center;
    color:#7f9bb5;
    font-size:12px;
    padding:40px 10px;
}

@media(max-width:900px) {
    .hero-title {font-size:30px;}
    .hero-features {flex-direction:column;}
    .credits-grid {grid-template-columns:1fr;}
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
        🎯 Smart recommendations<br>
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
    # SENTIMENT
    # --------------------------------------------------------

    if sentiment_results:
        positive = sum(
            1 for x in sentiment_results if "Positive" in x
        )
        negative = sum(
            1 for x in sentiment_results if "Negative" in x
        )
        neutral = sum(
            1 for x in sentiment_results if "Neutral" in x
        )

        total = len(sentiment_results)

        md('<div class="section-title">😊 Sentiment Analysis</div>')

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Positive", f"{positive / total * 100:.0f}%")

        with c2:
            st.metric("Neutral", f"{neutral / total * 100:.0f}%")

        with c3:
            st.metric("Negative", f"{negative / total * 100:.0f}%")

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    md('<div class="section-title">🎯 Recommended Movies</div>')
    md(
        '<div class="section-description">'
        'Movies recommended by TMDB based on the selected movie and its language.'
        '</div>'
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
                rec_rating = rec.get("vote_average", 0)
                rec_year = (rec.get("release_date") or "N/A")[:4]

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
            '🎯 No recommendations were found for this movie.'
            '</div>'
        )


# ============================================================
# HOME MOVIE SECTIONS
# ============================================================

md('<div class="cinema-line"></div>')


def display_movie_row(movies):
    if not movies:
        md(
            '<div class="info-box">'
            '🎬 No movies found right now. Please try again in a moment.'
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
            year = year[:4] if year != "N/A" else year

            movie_rating = movie_item.get("vote_average", 0)

            md(
                f"""
                <div class="movie-name">{movie_title}</div>
                <div class="movie-year">{year}</div>
                <div class="movie-rating">⭐ {movie_rating:.1f}</div>
                """
            )


# ------------------------------------------------------------
# LATEST
# ------------------------------------------------------------

with st.spinner(f"Loading latest {selected_language} movies..."):
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


# ------------------------------------------------------------
# TRENDING
# ------------------------------------------------------------

with st.spinner(f"Loading trending {selected_language} movies..."):
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


# ------------------------------------------------------------
# POPULAR
# ------------------------------------------------------------

with st.spinner(f"Loading popular {selected_language} movies..."):
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
        Search • Reviews • Sentiment • Recommendations •
        Cast & Crew • Latest • Trending • Popular
        <br><br>
        Movie information powered by TMDB
    </div>
    """
)
