import os
import requests

#
# Methods and variables related to communication with Okta
#

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
OKTA_API_TOKEN = os.getenv("OKTA_API_TOKEN")


def get_okta_user_id(email):
    url = f"{OKTA_DOMAIN}/api/v1/users/{email}"
    response_json = send_okta_request("GET", url)
    return response_json["id"]


def get_okta_factor_id(user_id):
    url = f"{OKTA_DOMAIN}/api/v1/users/{user_id}/factors"
    response_json = send_okta_request("GET", url)
    for factor in response_json:
        if factor["factorType"] == "push":
            return factor["id"]
    raise Exception(f"User {user_id} is not enrolled in Push Factor")


def send_okta_push_factor(user_id, factor_id):
    url = f"{OKTA_DOMAIN}/api/v1/users/{user_id}/factors/{factor_id}/verify"
    response_json = send_okta_request("POST", url)
    return response_json


def extract_transaction_id(response):
    return response["_links"]["poll"]["href"].split("/")[-1]


def poll_okta_result(user_id, factor_id, transaction_id):
    url = f"{OKTA_DOMAIN}/api/v1/users/{user_id}/factors/{factor_id}/transactions/{transaction_id}"
    response_json = send_okta_request("GET", url)
    return response_json


def send_okta_request(method, url):
    headers = {"accept": "application/json", "content-type" : "application/json", "authorization" : "SSWS " + OKTA_API_TOKEN}
    if method == "GET":
        response = requests.get(url, headers = headers)
    elif method == "POST":
        response = requests.post(url, headers = headers)
    else:
        raise Exception(f"Invalid HTTP Method {method}.")
    return response.json()