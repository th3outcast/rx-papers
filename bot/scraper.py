import requests
import urllib.parse
from bs4 import BeautifulSoup


API_URL = "https://api.semanticscholar.org/graph/v1"


"""
    Query semanticscholar.org api endpoint for paper
"""
def semantic_scholar_query(paper, limit=5, offset=0, timeout=5):
    params = {
        "query": paper,
        "offset": offset,
        "limit": limit,
    }

    # request paper from api endpoint
    r = requests.get(API_URL + "/paper/search",
            params=params,
            timeout=timeout)

    # parse json response
    if r.status_code == 200:
        data = r.json()
        if len(data) == 1 and 'error' in data:
            data = {}
    elif r.status_code == 429:
        raise ConnectionRefusedError("HTTP status 429: Too Many Requests.")
    return data


def parse_titles(res):
    base_url = "https://semanticscholar.org/paper/"

    # dictionary to hold titles and their links
    titles = {}

    for i in range(len(res['data'])):
        uri = res['data'][i]['title'].replace(" ", "-")
        uri += '/' + res['data'][i]['paperId']

        # parse special url characters
        titles[res['data'][i]['title']] = base_url + urllib.parse.quote(uri, safe='-/')

    return titles


def extract_download(url, timeout=5):
    links = []
    r = requests.get(url,
            timeout=timeout)
    result_html = BeautifulSoup(r.text, "html.parser")

    for i in result_html.findAll("a", {"data-selenium-selector" : "paper-link"}):
        links.append(
                i.get('href')
                )

    return links


def extract_paper_links(parsed_titles):
    paper_link_map = {}
    for k, v in parsed_titles.items():
        paper_link_map[k] = extract_download(v)

    return paper_link_map


if __name__ == "__main__":
    print()
