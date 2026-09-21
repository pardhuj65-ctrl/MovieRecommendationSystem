from sentiment import analyze_sentiment


reviews = [
    "This movie was absolutely amazing and fantastic!",
    "This movie was boring and terrible.",
    "The movie was okay."
]


for review in reviews:

    result = analyze_sentiment(review)

    print()
    print("Review:", review)
    print("Sentiment:", result)