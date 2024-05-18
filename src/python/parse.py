import requests
import hashlib


def get_page_hash(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                      '118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url=url, headers=headers)

        actual_hash = hashlib.md5(response.text.encode()).hexdigest()
    except requests.exceptions.MissingSchema:
        actual_hash = ''

    return actual_hash
