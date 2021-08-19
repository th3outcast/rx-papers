import requests

API_URL = "https://api.semanticscholar.org/graph/v1"

"""
    Query semanticscholar.org api endpoint for paper
"""
def semantic_scholar_query(paper):
    params = {
        "query": paper,
        "offset": 0,
        "limit": 5,
    }

    # request paper from api endpoint
    r = requests.get(API_URL + "/paper/search",
            params=params,
            timeout=3)

    # parse json response
    if r.status_code == 200:
        resp = r.json()
        if len(resp) == 1 and 'error' in data:
            resp = {}
    elif r.status_code == 429:
        raise ConnectionRefusedError("HTTP status 429: Too Many Requests.")
    return resp


if __name__ == "__main__":
