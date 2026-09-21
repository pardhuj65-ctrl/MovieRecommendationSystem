import streamlit as st
from movie_api import (
    search_movies,
    get_movie_details,
    get_movie_reviews,
    get_similar_movies,
    get_latest_movies,
    get_popular_movies,
    get_trending_movies,
)
from sentiment import analyze_sentiment

st.set_page_config(
    page_title="Movie AI Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
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
    font-size:27px;font-weight:900;color:#fff;
    text-shadow:0 0 8px rgba(60,190,255,.75),0 0 20px rgba(80,100,255,.45);
}
.sidebar-subtitle {color:#8edfff;font-size:12px;font-weight:600;margin-bottom:25px;}

.language-panel {
    background:linear-gradient(135deg,rgba(15,55,100,.95),rgba(20,25,70,.95));
    border:1px solid rgba(50,190,255,.55);
    border-radius:16px;padding:15px;margin-bottom:10px;
    box-shadow:0 0 22px rgba(0,160,255,.12);
}
.language-title {color:#8de9ff !important;font-size:17px;font-weight:900;}

div[data-baseweb="select"] > div {
    background:linear-gradient(135deg,#162e56,#173a69) !important;
    border:1px solid rgba(90,220,255,.65) !important;
    border-radius:11px !important;min-height:44px !important;
    box-shadow:0 0 15px rgba(0,180,255,.12);
}
div[data-baseweb="select"] span {color:#fff !important;font-weight:750 !important;}

.feature-title {color:#ffd84d !important;font-size:17px;font-weight:900;margin-bottom:15px;}
.feature-item {color:#d9efff !important;font-size:14px;font-weight:650;line-height:2.35;}

.hero {
    background:
        radial-gradient(circle at 10% 30%,rgba(20,130,255,.35),transparent 35%),
        radial-gradient(circle at 90% 60%,rgba(200,40,255,.22),transparent 35%),
        linear-gradient(135deg,rgba(7,37,85,.98),rgba(14,20,65,.98),rgba(35,10,65,.98));
    border:1px solid rgba(70,190,255,.55);border-radius:22px;
    padding:35px 25px 30px;margin-bottom:30px;
    box-shadow:0 15px 55px rgba(0,0,0,.45),inset 0 0 50px rgba(40,130,255,.08);
}
.hero-title {
    text-align:center;font-size:43px;font-weight:950;color:#fff;letter-spacing:1px;
    text-shadow:0 0 8px rgba(100,220,255,.85),0 0 25px rgba(80,120,255,.50);
}
.hero-title span {
    background:linear-gradient(90deg,#fff,#7eeaff,#c98cff);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.hero-subtitle {text-align:center;color:#e7f6ff;font-size:16px;font-weight:650;margin-top:7px;}
.hero-features {display:flex;justify-content:space-around;margin-top:28px;gap:10px;}
.hero-feature {text-align:center;color:#eaf8ff;font-weight:800;font-size:14px;}
.hero-icon {font-size:28px;display:block;margin-bottom:5px;}

.section-title {
    font-size:28px;font-weight:900;color:#fff;margin-top:30px;margin-bottom:7px;
    text-shadow:0 0 12px rgba(70,190,255,.35);
}
.section-title.latest {color:#28dcff;}
.section-title.trending {color:#ff72d7;}
.section-title.popular {color:#ffd34f;}
.section-description {color:#b8d8ef;font-size:14px;margin-bottom:15px;}

.stTextInput > div > div > input {
    background:rgba(8,20,40,.95) !important;color:#fff !important;
    border:1px solid rgba(70,190,255,.55) !important;
    border-radius:11px !important;font-size:16px !important;min-height:45px !important;
}
.stTextInput > div > div > input::placeholder {color:#8faac0 !important;}

.stButton > button {
    background:linear-gradient(90deg,#11bde5,#466eff,#9b35ff) !important;
    color:#fff !important;border:none !important;border-radius:11px !important;
    font-weight:850 !important;min-height:43px !important;
    box-shadow:0 5px 18px rgba(50,150,255,.20);
}
.stButton > button:hover {
    box-shadow:0 0 25px rgba(60,190,255,.45) !important;
}

.result-row {
    background:rgba(10,27,48,.82);border:1px solid rgba(70,170,230,.22);
    border-radius:12px;padding:10px 14px;margin-bottom:8px;
}
.result-title {color:#fff;font-size:16px;font-weight:850;}

.movie-name {color:#fff;font-size:15px;font-weight:850;margin-top:8px;min-height:40px;}
.movie-year {color:#9dbbd3;font-size:13px;}
.movie-rating {color:#ffd52f;font-size:14px;font-weight:850;}

.detail-box {
    background:linear-gradient(135deg,rgba(15,35,62,.97),rgba(5,15,29,.98));
    border:1px solid rgba(70,190,255,.30);border-radius:17px;padding:23px;
    box-shadow:0 12px 35px rgba(0,0,0,.30);
}
.detail-title {
    font-size:35px;font-weight:950;color:#fff;
    text-shadow:0 0 10px rgba(70,200,255,.30);
}
.detail-text {color:#d9ecfa;font-size:15px;line-height:1.7;}

.review-box {
    background:linear-gradient(135deg,rgba(13,32,53,.95),rgba(5,14,27,.98));
    border-left:4px solid #36cfff;border-radius:12px;padding:17px;margin-bottom:13px;
}
.review-author {color:#77dfff;font-weight:850;}
.review-text {color:#dcecf8;line-height:1.65;}

.info-box {
    background:linear-gradient(90deg,rgba(15,60,100,.80),rgba(40,35,100,.70));
    border:1px solid rgba(50,190,255,.25);border-radius:11px;padding:13px;
    color:#a9eaff;font-weight:650;
}
.cinema-line {
    height:1px;background:linear-gradient(90deg,transparent,rgba(60,190,255,.65),rgba(180,70,255,.55),transparent);
    margin:25px 0;
}
.footer {text-align:center;color:#7f9bb5;font-size:12px;padding:40px 10px;}

@media(max-width:900px) {
    .hero-title {font-size:30px;}
    .hero-features {flex-direction:column;}
}
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Hindi": "hi",
    "English": "en",
}

if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

with st.sidebar:
    st.markdown('<div class="sidebar-title">🎬 Movie AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Your Smart Movie Companion</div>', unsafe_allow_html=True)

    st.markdown('<div class="language-panel"><div class="language-title">🌐 Movie Language</div></div>', unsafe_allow_html=True)

    selected_language = st.selectbox(
        "Select language",
        list(LANGUAGES.keys()),
        index=0,
        label_visibility="collapsed",
    )
    language_code = LANGUAGES[selected_language]

    st.markdown("---")
    st.markdown("""
    <div class="feature-title">⭐ Features</div>
    <div class="feature-item">
    🔎 Search any movie<br>
    ⭐ Movie ratings<br>
    📝 Real movie reviews<br>
    😊 Sentiment analysis<br>
    🎯 Same-language recommendations<br>
    🆕 Latest language movies<br>
    🔥 Popular language movies<br>
    📈 Trending language movies
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<div style="color:#9cc8df;font-size:12px;text-align:center;padding-top:15px;">'
        '🎬 Movie information<br>powered by TMDB</div>',
        unsafe_allow_html=True,
    )

st.markdown("""
<div class="hero">
    <div class="hero-title">🎬 MOVIE <span>AI ASSISTANT</span></div>
    <div class="hero-subtitle">
        Discover movies • Read real reviews • Analyze sentiment • Get intelligent recommendations
    </div>
    <div class="hero-features">
        <div class="hero-feature"><span class="hero-icon">🔎</span>Search<br>Any Movie</div>
        <div class="hero-feature"><span class="hero-icon">⭐</span>Real<br>Reviews</div>
        <div class="hero-feature"><span class="hero-icon">💗</span>Sentiment<br>Analysis</div>
        <div class="hero-feature"><span class="hero-icon">✨</span>Smart<br>Recommendations</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">🔎 Search Any Movie</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Search for any movie from the TMDB database.</div>', unsafe_allow_html=True)

search_col1, search_col2 = st.columns([5, 1])

with search_col1:
    movie_name = st.text_input(
        "Movie name",
        placeholder="Example: KGF, RRR, Salaar, Hanuman...",
        label_visibility="collapsed",
    )

with search_col2:
    search_clicked = st.button("🔎 Search Movie", use_container_width=True)

if search_clicked:
    if not movie_name.strip():
        st.warning("Please enter a movie name.")
    else:
        with st.spinner("🎬 Searching TMDB..."):
            try:
                results = search_movies(movie_name.strip())
            except Exception:
                results = []
        st.session_state.search_results = results[:8]
        st.session_state.selected_movie = None

if st.session_state.search_results:
    st.markdown('<div class="section-title">🎞️ Search Results</div>', unsafe_allow_html=True)

    for index, movie in enumerate(st.session_state.search_results):
        title = movie.get("title") or movie.get("original_title") or "Unknown"
        release_date = movie.get("release_date") or "N/A"
        rating = movie.get("vote_average", 0)

        col1, col2, col3, col4 = st.columns([4.5, 1.5, 1, 1.5])

        with col1:
            st.markdown(
                f'<div class="result-row"><div class="result-title">🎬 {title}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.write(f"📅 {release_date}")
        with col3:
            st.write(f"⭐ {rating:.1f}")
        with col4:
            if st.button("View Details", key=f"details_{movie.get('id')}_{index}", use_container_width=True):
                with st.spinner("Loading movie..."):
                    details = get_movie_details(movie.get("id"))
                st.session_state.selected_movie = details
                st.rerun()

movie = st.session_state.selected_movie

if movie:
    movie_id = movie.get("id")
    title = movie.get("title") or "Unknown"
    poster_path = movie.get("poster_path")
    poster_url = "https://image.tmdb.org/t/p/w500" + poster_path if poster_path else None
    rating = movie.get("vote_average", 0)
    release_date = movie.get("release_date") or "N/A"
    original_language = (movie.get("original_language") or "N/A").upper()
    runtime = movie.get("runtime", 0)
    overview = movie.get("overview", "No overview available.")
    genres = movie.get("genres", [])
    genre_names = ", ".join(g.get("name", "") for g in genres)

    st.markdown('<div class="section-title">🎬 Movie Details</div>', unsafe_allow_html=True)
    detail_col1, detail_col2 = st.columns([1, 2])

    with detail_col1:
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.info("Poster not available.")

    with detail_col2:
        st.markdown(
            f"""
            <div class="detail-box">
                <div class="detail-title">{title}</div><br>
                <div class="detail-text">
                    ⭐ <b>Rating:</b> {rating:.1f}/10<br><br>
                    📅 <b>Release Date:</b> {release_date}<br><br>
                    🌐 <b>Original Language:</b> {original_language}<br><br>
                    ⏱️ <b>Runtime:</b> {runtime} minutes<br><br>
                    🎭 <b>Genres:</b> {genre_names or "N/A"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">📖 Overview</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="detail-box"><div class="detail-text">{overview}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">💬 Movie Reviews</div>', unsafe_allow_html=True)

    with st.spinner("Loading real TMDB reviews..."):
        try:
            reviews = get_movie_reviews(movie_id)
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

            st.markdown(
                f"""
                <div class="review-box">
                    <div class="review-author">👤 {author}</div><br>
                    <div class="review-text">{content}</div><br>
                    <b>Sentiment:</b> {sentiment}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="info-box">💬 No TMDB reviews are available for this movie right now.</div>',
            unsafe_allow_html=True,
        )

    if sentiment_results:
        positive = sum(1 for x in sentiment_results if "Positive" in x)
        negative = sum(1 for x in sentiment_results if "Negative" in x)
        neutral = sum(1 for x in sentiment_results if "Neutral" in x)
        total = len(sentiment_results)

        st.markdown('<div class="section-title">😊 Sentiment Analysis</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Positive", f"{positive / total * 100:.0f}%")
        with c2:
            st.metric("Neutral", f"{neutral / total * 100:.0f}%")
        with c3:
            st.metric("Negative", f"{negative / total * 100:.0f}%")

    st.markdown('<div class="section-title">🎯 Recommended Movies</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Recommendations are based on the selected movie and its language.</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Finding similar movies..."):
        try:
            recommendations = get_similar_movies(movie_id)
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

                st.markdown(
                    f"""
                    <div class="movie-name">{rec_title}</div>
                    <div class="movie-year">{rec_year}</div>
                    <div class="movie-rating">⭐ {rec_rating:.1f}</div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            '<div class="info-box">🎯 No same-language recommendations were found for this movie.</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div class="cinema-line"></div>', unsafe_allow_html=True)


def display_movie_row(movies):
    if not movies:
        st.markdown(
            '<div class="info-box">🎬 No movies found right now. Please try again in a moment.</div>',
            unsafe_allow_html=True,
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
                st.markdown(
                    """
                    <div style="height:260px;display:flex;align-items:center;
                    justify-content:center;background:#08182d;border-radius:12px;color:#789;">
                    🎬 No Poster
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            movie_title = (
                movie_item.get("title")
                or movie_item.get("original_title")
                or "Unknown"
            )
            year = movie_item.get("release_date") or "N/A"
            year = year[:4] if year != "N/A" else year
            movie_rating = movie_item.get("vote_average", 0)

            st.markdown(
                f"""
                <div class="movie-name">{movie_title}</div>
                <div class="movie-year">{year}</div>
                <div class="movie-rating">⭐ {movie_rating:.1f}</div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# LATEST
# ============================================================

with st.spinner(f"Loading latest {selected_language} movies..."):
    try:
        latest_movies = get_latest_movies(language_code)
    except Exception:
        latest_movies = []

st.markdown(
    f"""
    <div class="section-title latest">🆕 Latest {selected_language} Movies</div>
    <div class="section-description">
        Recently released {selected_language} movies
    </div>
    """,
    unsafe_allow_html=True,
)
display_movie_row(latest_movies)


# ============================================================
# TRENDING
# ============================================================

with st.spinner(f"Loading trending {selected_language} movies..."):
    try:
        trending_movies = get_trending_movies(language_code)
    except Exception:
        trending_movies = []

if not trending_movies:
    try:
        trending_movies = get_popular_movies(language_code)
    except Exception:
        trending_movies = []

st.markdown(
    f"""
    <div class="section-title trending">🔥 Trending {selected_language} Movies</div>
    <div class="section-description">
        Currently popular {selected_language} movies
    </div>
    """,
    unsafe_allow_html=True,
)
display_movie_row(trending_movies)


# ============================================================
# POPULAR
# ============================================================

with st.spinner(f"Loading popular {selected_language} movies..."):
    try:
        popular_movies = get_popular_movies(language_code)
    except Exception:
        popular_movies = []

st.markdown(
    f"""
    <div class="section-title popular">⭐ Popular {selected_language} Movies</div>
    <div class="section-description">
        Most popular {selected_language} movies on TMDB
    </div>
    """,
    unsafe_allow_html=True,
)
display_movie_row(popular_movies)


st.markdown(
    """
    <div class="footer">
        🎬 <b>Movie AI Assistant</b><br><br>
        Search • Reviews • Sentiment • Recommendations • Latest • Trending
        <br><br>
        Movie information powered by TMDB
    </div>
    """,
    unsafe_allow_html=True,
)
