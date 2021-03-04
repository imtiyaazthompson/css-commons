import config
import searchkey as sk
import json
import requests

# Example API request: https://api.stackexchange.com/2.2/tags?order=desc&sort=popular&site=stackoverflow

API_KEY = config.api_key
SECRET = config.secret_key
API = "https://api.stackexchange.com/2.2/"
rparams = {
    "site": "stackoverflow",
    "page": 1,
    "pagesize": 100,
}

faq = []


# Perform a GET request given a URL and search parameters
def get(url):
    resp = requests.get(url,params=rparams)
    return resp.json()


# Get a list of all the tags available on stack overflow
def get_tags():
    request_url = API + sk.search["tags"]
    print(get(request_url))


# Get a list of all the tags related to the specified tag
def get_related_tags(tag):
    request_url = API + "tags/" + tag + "/" + sk.search["related"]
    print(get(request_url))


# Get a list of the frequently asked questions based on a specific tag
# Does so for 100 results of a specific page
# Calling function will advance the page and keep track of remaining request quota
# Pagination call: https://api.stackexchange.com/2.2/tags/css/faq?page=1&pagesize=100&site=stackoverflow
def get_tag_faq(tag):
    request_url = API + "tags/" + tag + "/" + sk.search["faq"]
    response = get(request_url)

    #show_keys(response)

    for item in response["items"]:
        faq.append({
            "tags": item["tags"],
            "is_answered": item["is_answered"],
            "score": item["score"],
            "question_id": item["question_id"],
            "answer_id": item["accepted_answer_id"],
            "title": item["title"],
            "link": item["link"],
            "last_updated": item["last_edit_date"]
        })


    return (response["has_more"], response["quota_remaining"])


def load_json():
    with open("faq.json", "r") as faq:
        loaded_json = json.load(faq)
        print(loaded_json)


def show_keys(json):
    print(json.keys())


def main():
    rq = -1
    has_more = True
    while rq != 0 and has_more:
        has_more, rq = get_tag_faq("css")
        print(f"Processed page [{rparams.page}], Quota remaining [{rq}]")
        rparams["page"] = rparams["page"] + 1

    with open("faq.json", "a") as out:
        json.dump({"details": faq}, out)


if __name__ == '__main__':
    main()
