import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load movie data
movies = pd.read_csv("movies.csv")


# Replace missing descriptions with empty text
movies["description"] = movies["description"].fillna("")


# Convert movie descriptions into numerical values
vectorizer = TfidfVectorizer(stop_words="english")

tfidf_matrix = vectorizer.fit_transform(movies["description"])


# Calculate similarity between movies
similarity = cosine_similarity(tfidf_matrix)


# Recommendation function
def recommend(movie_title):

    if movie_title not in movies["title"].values:
        print("Movie not found.")
        return

    movie_index = movies[movies["title"] == movie_title].index[0]

    similarity_scores = list(enumerate(similarity[movie_index]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommended_movies = similarity_scores[1:6]

    print("\nRecommended movies for:", movie_title)

    for index, score in recommended_movies:
        print(movies.iloc[index]["title"])


# Ask user for a movie
movie = input("Enter a movie name: ")

recommend(movie)