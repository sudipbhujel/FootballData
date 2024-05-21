import requests
from urllib.parse import parse_qs
import requests
import json
import yaml
import csv
import xmltodict

REQUEST_MAX_RETRY = 3
request_retry_count = 0

def get_data_from_url(url, headers, params):
    global request_retry_count

    response = requests.get(url, headers=headers, params=params, timeout = 10)
    content_type = response.headers["Content-Type"]

    if response.status_code != 200:
        if request_retry_count < REQUEST_MAX_RETRY:
            request_retry_count += 1
            get_data_from_url(url, headers, params)
        else:
            raise requests.exceptions.RequestException(response.status_code)

    # application based content types
    if content_type.startswith("application/json"):
        response = json.loads(response.text)

    elif content_type.startswith("application/xml"):
        response = xmltodict.parse(response.text)
    
    elif content_type.startswith("application/x-www-form-urlencoded"):
        response = parse_qs(response.text)
    
    elif content_type.startswith("application/yaml"):
        response = yaml.load(response.text, Loader=yaml.Loader)
    
    # text based content types
    elif content_type.startswith("text/plain"):
        response = response.text
    
    elif content_type.startswith("text/csv"):
        response = csv.DicReader(response.text)

    elif content_type.startswith("text/html"):
        response = response.text

    
    # retry cycle
    if response == None or response == "":
        if request_retry_count < REQUEST_MAX_RETRY:
            request_retry_count += 1
            response = get_data_from_url(url, headers, params)
        else:
            response = ""
    else:
        request_retry_count = 0
    
    return response