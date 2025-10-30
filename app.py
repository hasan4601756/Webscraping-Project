from flask import Flask, render_template, request, redirect, url_for, flash
from search import fetch_blog_links
from scrapper import extract_article_and_comments
from gpt import get_summary
from sentiment_analyzer import sentiment_scores
from graph import generate_pie_chart, generate_wordcloud
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if not keyword:
            flash("Please enter a keyword.", "warning")
            return redirect(url_for('index'))

        try:
            blogs = fetch_blog_links(keyword)
            if not blogs:
                flash("No blogs found for this keyword.", "info")
                blogs = []
            return render_template('index.html', blogs=blogs)

        except Exception as e:
            flash(f"An error occurred while fetching blogs: {str(e)}", "danger")
            return render_template('index.html', blogs=[])

    return render_template('index.html')


@app.route('/blog_description/', methods=["GET"])
def blog_description():

    try:
        url = request.args.get('url')
        if not url:
            flash("No blog URL provided.", "warning")
            return redirect(url_for('index'))

        try:
            blog = extract_article_and_comments(url)
        except Exception as e:
            flash(f"Failed to extract blog content: {str(e)}", "danger")
            return redirect(url_for('index'))

        content = blog.get('text', '')
        comments = set(blog.get('comments', []))

        if not content:
            flash("No main content found for this blog.", "warning")

        try:
            summary = get_summary(content) if content else "No content available for summarization."
        except Exception as e:
            summary = "Error while generating summary."

        try:
            wordcloud = generate_wordcloud(content)
            wordcloud_path = os.path.join('static', 'img', 'wordcloud.png')
            wordcloud.savefig(wordcloud_path)
            wordcloud.close()
        except Exception as e:
            flash("Could not generate wordcloud.", "warning")

        comment_dicts = []
        if comments:
            try:
                for comment in list(comments):
                    sentiment = sentiment_scores(comment)
                    comment_dicts.append({'content': comment, 'sentiment': sentiment})
            except Exception as e:
                flash(f"Error during sentiment analysis: {str(e)}", "warning")

            try:
                plot = generate_pie_chart(comment_dicts)
                plot_path = os.path.join('static', 'img', 'plot.png')
                plot.savefig(plot_path)
                plot.close()
            except Exception as e:
                flash("Could not generate sentiment chart.", "warning")
        else:
            pass

        return render_template(
            'blog_description.html',
            summary=summary,
            comments=comment_dicts
        )

    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for('index'))

    
if __name__ == '__main__':
    app.run(debug=True)