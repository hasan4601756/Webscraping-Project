import requests
import trafilatura
from google import genai
import os
import openai
# from bs4 import BeautifulSoup

# headers = {
#     "User-Agent": "Mozilla/5.0 (compatible; MalihaBot/1.0; +https://yourdomain.com/bot-info)"
# }

# response = requests.get('https://medium.com/life-hacks-for-business/12-lessons-of-waking-up-at-4-30-a-m-for-21-days-90d1053c3634', headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')
# body = soup.body
# bscontent = body.get_text()

# client = genai.Client(api_key=os.environ.get('AI_studio_api_key'))


# links = ['https://www.reddit.com/r/MachineLearning/comments/1fsv7js/discussion_what_are_some_the_informative_blogs_on/', 'https://blog.ml.cmu.edu/', 'https://www.tableau.com/learn/articles/blogs-about-machine-learning-artificial-intelligence', 'https://machinelearning.apple.com/', 'https://blog.gregbrockman.com/how-i-became-a-machine-learning-practitioner', 'https://cloud.google.com/blog/products/ai-machine-learning', 'https://blogs.oracle.com/machinelearning/', 'https://ischoolonline.berkeley.edu/blog/what-is-machine-learning/', 'https://brenocon.com/blog/2008/12/statistics-vs-machine-learning-fight/', 'https://news.ycombinator.com/item?id=34198427']

# for link in links:
#     content = trafilatura.fetch_url(link)

#     content = trafilatura.extract(content)

#     response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=f'Make a summary of the content given \'\'\'{content}\'\'\''
#     )
#     print(response.text)



def get_summary(content):
    PROMPT = f'Generate a precise summary of the given content in such way that it covers what is discussed in it Content: \'\'\'{content}\'\'\' Please give output in plain text with no headings etc'
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROMPT
        )

        summary = response.text
    except:
        response = openai.completions.create(
            model='text-davinci-003',
            prompt= PROMPT
        )

        summary = response.choices[0].text.strip()

    return summary