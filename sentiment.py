from nltk.sentiment import SentimentIntensityAnalyzer


# Create VADER analyzer
sia = SentimentIntensityAnalyzer()


def analyze_sentiment(text):

    if not text:
        return "Neutral 😐"

    scores = sia.polarity_scores(text)

    compound = scores["compound"]

    if compound >= 0.05:

        return "Positive 😊"

    elif compound <= -0.05:

        return "Negative 😞"

    else:

        return "Neutral 😐"


def get_sentiment_score(text):

    if not text:
        return 0.0

    scores = sia.polarity_scores(text)

    return scores["compound"]