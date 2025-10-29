from flask import Flask, request, render_template
from search import fetch_blog_links
from scrapper import extract_article_and_comments
from gpt import get_summary
from sentiment_analyzer import sentiment_scores

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        blogs = fetch_blog_links(keyword)

        return render_template('index.html', blogs=blogs)
    else:
        return render_template('index.html')

@app.route('/blog_description/', methods=["GET"])
def blog_description():
    url = request.args.get('url')
    blog = extract_article_and_comments(url)
    content = blog['text']
    comments = blog['comments']

    summary = get_summary(content)

    comment_dicts = []

    for comment in comments:
        comment_sentiment = sentiment_scores(comment)
        comment_dict = {'content': comment, 'sentiment': comment_sentiment}
        comment_dicts.append(comment_dict)

    return render_template('blog_description.html', summary=summary, comments=comment_dicts)
    
if __name__ == '__main__':
    app.run(debug=True)