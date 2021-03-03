import config
import searchkey as sk
import json
import requests

# Example API request: https://api.stackexchange.com/2.2/tags?order=desc&sort=popular&site=stackoverflow

API_KEY = config.api_key
SECRET = config.secret_key
API = "https://api.stackexchange.com/2.2/"
rparams = {
    "site": "stackoverflow"
}

def get(url):
    resp = requests.get(url,params=rparams)
    return resp.json()


def request_tags():
    request_url = API + sk.search["tags"]
    print(get(request_url))


def main():
    request_tags()


if __name__ == '__main__':
    main()
