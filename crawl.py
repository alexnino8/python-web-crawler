import urllib.parse
from bs4 import BeautifulSoup, Tag



# this function normalizes the url provided stripping the protocol and any trailing slashes
def normalize_url(url: str) -> str:
    url_obj = urllib.parse.urlsplit(url)
    netloc = url_obj.netloc
    path = url_obj.path

    if path[-1] == "/":
        path = path [:-1]

    normalized_url = netloc + path

    return normalized_url

# this function will return the h1 with fallback to h2 
def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    heading = ""
    if soup.h1 != None:
        heading = str(soup.h1.string)
    else:
        if soup.h2 != None:
            heading = str(soup.h2.string)

    return heading

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    if soup.main != None:
        first_p = soup.main.p
    else: 
        first_p = soup.p
    
    if first_p != None:
        return str(first_p.string)
        
    return ""
    
