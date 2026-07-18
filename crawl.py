import urllib.parse

def normalize_url(url):
    url_obj = urllib.parse.urlsplit(url)
    netloc = url_obj.netloc
    path = url_obj.path

    if path[-1] == "/":
        path = path [:-1]

    normalized_url = netloc + path

    return normalized_url


