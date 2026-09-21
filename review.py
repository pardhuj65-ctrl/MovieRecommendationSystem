def analyze_review(review):

    positive_words = [
        "good",
        "great",
        "amazing",
        "excellent",
        "fantastic",
        "wonderful",
        "love",
        "loved",
        "best",
        "awesome"
    ]

    negative_words = [
        "bad",
        "worst",
        "boring",
        "terrible",
        "awful",
        "hate",
        "hated",
        "poor",
        "disappointing"
    ]

    words = review.lower().split()

    positive_count = 0
    negative_count = 0

    for word in words:

        if word in positive_words:
            positive_count += 1

        if word in negative_words:
            negative_count += 1

    if positive_count > negative_count:
        return "Positive 😊"

    elif negative_count > positive_count:
        return "Negative 😞"

    else:
        return "Neutral 😐"


review = input("Enter your movie review: ")

result = analyze_review(review)

print("Sentiment:", result)