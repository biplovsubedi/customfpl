import requests
import json


def request_data_from_url(url):
    """Takes a url as an input and fetches JSON data
    to that URL
    Converts JSON to dictionary and returns that to the user.format()

    Args:
        url (string): Complete url of API endpoint

    Returns:
        dict: api response data, None if error
    """
    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        return None
    print(res)
    if res.status_code != 200:
        return None

    return json.loads(res.text)
