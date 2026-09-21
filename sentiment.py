from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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