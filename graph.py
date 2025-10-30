import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from wordcloud import WordCloud

def generate_pie_chart(comment_dict):
    comment_list = {key: [d[key] for d in comment_dict] for key in comment_dict[0]}
    
    sentiment_counts = {}
    for sentiment in comment_list['sentiment']:
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    plt.figure(figsize=(6, 6))
    plt.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%')
    plt.title("Sentiment Distribution")

    return plt

def generate_wordcloud(content):
    wordcloud = WordCloud(
        width=1000,
        height=600,
        background_color="white",
        max_words=100,
        colormap="viridis"
    ).generate(content)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    return plt

# def generate_wordcloud(comments):
#     if not comments:
#         print("No comments found.")
#         return

#     cleaned_comments = [c.strip().lower() for c in comments if c and len(c.strip()) > 5]

#     unique_comments = []
#     for c in cleaned_comments:
#         if not any(c in other for other in cleaned_comments if c != other):
#             unique_comments.append(c)

#     text = " ".join(unique_comments)

#     wordcloud = WordCloud(
#         width=1000,
#         height=600,
#         background_color="white",
#         max_words=200,
#         colormap="viridis"
#     ).generate(text)

    # plt.figure(figsize=(10, 6))
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")
    # plt.title("Word Cloud of Blog Comments", fontsize=16)
    # return plt