import config
import searchkey as sk
import json
import requests
import time
import traceback

# Example API request: https://api.stackexchange.com/2.2/tags?order=desc&sort=popular&site=stackoverflow

API_KEY = config.api_key
SECRET = config.secret_key
API = "https://api.stackexchange.com/2.2/"
qparams = {
    "key": API_KEY,
    "site": "stackoverflow",
    "page": 1,
    "pagesize": 100,
    "filter": "!-NChB_2XN8edH-0g63JoXl1a4d)x*wJYq",
}

aparams = {
    "key": API_KEY,
    "site": "stackoverflow",
    "filter": "!9_bDE(fI5",
}

# Hold all details from a call to the API
faq = []
ans = []


# Perform a GET request given a URL and search parameters
def get(url, p):
    resp = requests.get(url,params=p)
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
# Edited to use custom lag to get all relevant information
def get_tag_faq(tag):
    request_url = API + "tags/" + tag + "/" + sk.search["faq"]
    response = get(request_url,qparams)

    # Extract Data
    # Provide checks for a key that may not be present in response
    for item in response["items"]:
        detail = {}
        if "tags" in item.keys():
            detail["tags"] = item["tags"]
        else:
            detail["tags"] = None
        if "is_answered" in item.keys():
            detail["is_answered"] = item["is_answered"]
        else:
            detail["is_answered"] = None
        if "score" in item.keys():
            detail["score"] = item["score"]
        else:
            detail["score"] = None
        if "question_id" in item.keys():
            detail["question_id"] = item["question_id"]
        else:
            detail["question_id"] = None
        if "accepted_answer_id" in item.keys():
            detail["answer_id"] = item["accepted_answer_id"]
        else:
            detail["answer_id"] = None
        if "title" in item.keys():
            detail["title"] = item["title"]
        else:
            detail["title"] = None
        if "link" in item.keys():
            detail["link"] = item["link"]
        else:
            detail["link"] = None
        if "last_edit_date" in item.keys():
            detail["last_updated"] = item["last_edit_date"]
        else:
            detail["last_updated"] = None
        if "body" in item.keys():
            detail["body"] = item["body"]
        else:
            detail["body"] = None

        faq.append(detail)


    return (response["has_more"], response["quota_remaining"])


def get_answers():
    ids = chain_ids() # used to chain Answer Ids together for api request
    request_url = API + "answers/" + ids + "?"
    response = get(request_url,aparams)

    for item in response["items"]:
        detail = {}
        if "body" in item.keys():
            detail["body"] = item["body"]
        else:
            detail["body"] = None
        if "answer_id" in item.keys():
            detail["answer_id"] = item["answer_id"]
        else:
            detail["answer_id"] = None

        ans.append(detail)

    return response["quota_remaining"]


def load_json():
    with open("faq.json", "r") as faq:
        loaded_json = json.load(faq)
        print(loaded_json)


def collect_faq():
    rq = -1
    has_more = True

    try:
        while rq != 0 and has_more:
            has_more, rq = get_tag_faq("css")
            curr_page = qparams["page"]
            print(f"Processed page [{curr_page}], Quota remaining [{rq}]")
            qparams["page"] = qparams["page"] + 1

        curr_page = qparams["page"]
        print(f"\n\nData Collection Complete!\nPage Bookmark [{curr_page}]\nRemaining Quota [{rq}]")
    except KeyboardInterrupt as k:
        print("Program halted!")
        print(f"\n\nData Collection Interrupted!\nPage Bookmark [{curr_page}]\nRemaining Quota [{rq}]")
    except Exception as e:
        print("Some error occured!")
        print(e)
        print(f"\n\nData Collection Interrupted!\nPage Bookmark [{curr_page}]\nRemaining Quota [{rq}]")
    finally:
        with open("faq.json", "a") as out:
            json.dump({"details": faq}, out)
        print("\nJSON dumped to file")


# Given the answer IDs collected in faq.json, make API calls to get the answer bodies
# Upto 100 semicolon delimited IDs
# Read the JSON, buffer 100 Answer IDs, flush that buffer to make an API request, Collect, Repeat
def collect_anwswers():



def main():
     collect_faq()


if __name__ == '__main__':
    main()
