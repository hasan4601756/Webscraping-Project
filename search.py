import requests
import os

API_KEY = os.environ.get('google_api_key')
CX = os.environ.get('google_cx')

def fetch_blog_links(keyword, num_results=10):
    results = []
    start = 1

    while len(results) < num_results:
        url = 'https://www.googleapis.com/customsearch/v1'

        params = {
            'q': f'{keyword} ("blog post" OR inurl:blog OR site:medium.com OR site:wordpress.com OR site:blogspot.com OR site:substack.com OR site:dev.to) -site:facebook.com -site:youtube.com -site:twitter.com',

            'num': 10,
            'start': start
        }


        response = requests.get(url, params=params)
        data = response.json()

        if 'items' not in data:
            break
        for item in data['items']:
            results.append({'title': item['title'], 'link': item['link']})

        start += 10
    
    return results[:num_results]

if __name__ == '__main__':
    links = fetch_blog_links('machine learning', num_results=10)
    for i, link in enumerate(links, 1):
        print(f'{i}. {link}')