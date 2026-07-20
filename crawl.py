import urllib.parse
from typing import TypedDict
from bs4 import BeautifulSoup, Tag
import requests


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]



# this function normalizes the url provided stripping the protocol and any trailing slashes
def normalize_url(url: str) -> str:
    url_obj = urllib.parse.urlsplit(url)
    netloc = url_obj.netloc
    path = url_obj.path

    if path and path[-1] == "/":
        path = path [:-1]

    normalized_url = netloc + path

    return normalized_url.lower()

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

# this function will return the first paragraph inside main tag
# with fallback to the first paragraph 
# or an empty string of there is no paragraph tags
def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    if soup.main != None:
        first_p = soup.main.p
    else: 
        first_p = soup.p
    
    if first_p != None:
        return str(first_p.string)
        
    return ""

# this function extracts all urls in <a> tags that have a href attribute
def get_urls_from_html(html: str, base_url: str) -> list[str]:
    urls = []
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        if not isinstance(link, Tag):
            continue
        href = str(link['href'])
        if href.startswith(base_url):
            urls.append(href)
        else:
            try:
                urls.append(urllib.parse.urljoin(base_url, href))
            except Exception as e:
                 print(f"{str(e)}: {href}")
    return urls

# this function extracts the image urls found within the html
def get_images_from_html(html: str, base_url: str) -> list[str]:
    image_links = []
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img', src=True)
    for img in images:
        if not isinstance(img, Tag):
            continue
        src = str(img['src'])
        if src.startswith(base_url):
            image_links.append(src)
        else:
            try:
                image_links.append(urllib.parse.urljoin(base_url, src))
            except Exception as e:
                print(f"{str(e)}: {src}")   

    return image_links

# this function extracts the heading, first p, urls and image links 
# from a provided page_url
def extract_page_data(html: str, page_url: str) -> PageData:
    page_data : PageData = {
        "url": page_url,
        "heading": "",
        "first_paragraph": "",
        "outgoing_links": [],
        "image_urls": []
    }

    page_data['heading'] = get_heading_from_html(html)
    page_data['first_paragraph'] = get_first_paragraph_from_html(html)
    page_data['outgoing_links'] = get_urls_from_html(html, page_url)
    page_data['image_urls'] = get_images_from_html(html, page_url)

    return page_data

# this function returns the html of a provided url
def get_html(url: str) -> str:
    headers = {'user-agent': "BootCrawler/1.0"}

    r = requests.get(url, headers=headers)
    if r.status_code >= 400:
        raise Exception(f"Client/Server error: {r.status_code}")
    
    if not r.headers.get('Content-Type', '').startswith('text/html'):
        raise Exception(f"not html: {r.headers.get('Content-Type')}")

    return r.text

def crawl_page(base_url: str, current_url: str | None=None, page_data: dict[str,PageData] | None=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    if urllib.parse.urlparse(current_url).hostname != urllib.parse.urlparse(base_url).hostname:
        return
    
    normalized_url = normalize_url(current_url)
    if normalized_url in page_data:
        return
    try:
        html = get_html(current_url)
        print(f"crawling: {current_url}")
    except Exception as e:
        print(f"skipping {current_url}: {e}")
        return
    
    
    rich_data = extract_page_data(html, current_url)
    page_data[normalized_url] = rich_data

    for link in rich_data['outgoing_links']:
        crawl_page(base_url, link, page_data)

    



