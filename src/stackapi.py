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
rparams = {
    "key": API_KEY,
    "site": "stackoverflow",
    "page": 1,
    "pagesize": 100,
    "filter": "withbody",
}

# Hold all details from a call to the API
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

        faq.append(detail)


    return (response["has_more"], response["quota_remaining"])


def get_q(qid):
    request_url = API + f"questions/{qid}?"
    response = get(request_url)

    if "items" in response.keys():
        question = response["items"][0]["body"]
        return (qid,question)
    else:
        return (-1, -1)

def get_a(aid):
    request_url = API + f"answers/{aid}?"
    response = get(request_url)

    if "items" in response.keys():
        answer = response["items"][0]["body"]
        return (aid,answer)
    else:
        return (-1, -1)


def load_json():
    with open("faq.json", "r") as faq:
        loaded_json = json.load(faq)
        print(loaded_json)


def show_keys(json):
    print(json.keys())


def collect_faq():
    rq = -1
    has_more = True

    try:
        while rq != 0 and has_more:
            has_more, rq = get_tag_faq("css")
            curr_page = rparams["page"]
            print(f"Processed page [{curr_page}], Quota remaining [{rq}]")
            rparams["page"] = rparams["page"] + 1

        curr_page = rparams["page"]
        print(f"\n\nData Collection Complete!\nPage Bookmark [{curr_page}]\nRemaining Quota [{rq}]")
    except KeyboardInterrupt as k:
        print("Program halted!")
        print(f"\n\nData Collection Interrupted!\nPage Bookmark [{curr_page}]\nRemaining Quota [{rq}]")
    except Exception as e:
        print("Some error occured!")
        print(e)
        print(f"\n\nData Collection Interrupted!\nPage Bookmark [{curr_page}]\nRemaining Quota [{rq}]")
    finally:
        with open("faq2.json", "a") as out:
            json.dump({"details": faq}, out)
        print("\nJSON dumped to file")


def collect_qa():
    # load json
    with open("faq.json", "r") as jfaq:
        faqs = json.load(jfaq)

    # Open file for reading encountered ids
    f = open("enc.txt", "a").close()
    f = open("enc.txt", "r")
    processed = f.readlines()
    for j in range(len(processed)): processed[j] = processed[j].strip()
    f.close()

    f = open("enc.txt", "a")
    print(processed)
    ids = []

    try:
        qa_bodies = []
        i = 1
        for qa in faqs["details"]:
            if str(qa["question_id"]) in processed or str(qa["answer_id"]) in processed:
                print("ID already encountered!")
                continue

            if qa["is_answered"]:
                time.sleep(1)
                qid, q = get_q(qa["question_id"])
                aid, a = get_a(qa["answer_id"])

                # Some API responses may not return any information
                if (qid == -1) or (aid == -1):
                    print("Missing information encountered!")
                    continue

                ids.append(qid)
                ids.append(aid)

                print(f"Processed QA [{i}]/[49300]")
                i += 1

                details = {
                    "question_id": qid,
                    "question": q,
                    "answer_id": aid,
                    "answer": a
                }

                qa_bodies.append(details)

        print("QA Collection complete!")
    except KeyboardInterrupt as k:
        print("Program halted!")
    except Exception as e:
        print("Some error occured!")
        traceback.print_exc(e)
    finally:
        print(f"Processed [{i}] QAs")
        with open("qab.json", "a") as qab:
            json.dump({"details": qa_bodies}, qab)
            generate_encounter_ids(f, ids)
        print("QA Collection successfully dumped!")


def generate_encounter_ids(f, ids):
    for id in ids:
        f.write(f"{id}\n")

    f.close()


def main():
     # collect_faq()
     collect_qa()


if __name__ == '__main__':
    main()
