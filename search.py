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
            'q': (
                f'{keyword} ("blog post" OR "posted on" OR "written by" OR inurl:blog OR "comments") '
                '-category -tag -archive '
                '(site:medium.com OR site:substack.com OR site:wordpress.com OR site:blogspot.com '
                'OR site:dev.to OR site:hashnode.dev OR site:ghost.io OR site:vocal.media '
                'OR site:beehiiv.com OR site:mirror.xyz OR site:hubspot.com OR site:moz.com '
                'OR site:ahrefs.com OR site:buffer.com OR site:shopify.com OR site:semrush.com) '
                '-site:pinterest.* -site:facebook.com -site:youtube.com -site:twitter.com -site:reddit.com -site:quora.com'
            ),
            'num': 10,                  
            'start': start,
            'sort': 'date'          
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