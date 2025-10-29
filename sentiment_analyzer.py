from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def sentiment_scores(sentence):
    sid = SentimentIntensityAnalyzer()

    sentiment = sid.polarity_scores(sentence)

    if sentiment['compound'] >= 0.05:
        return 'Positive'
    elif sentiment['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'
    
if __name__ == '__main__':
    print(f'Overall Sentiment: {sentiment_scores('Pakistan is the richest country in the world if you know it.')}')