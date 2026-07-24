import urllib.parse
from typing import TypedDict, Optional, Any
from bs4 import BeautifulSoup, Tag
import requests
import asyncio
import aiohttp



class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

class AsyncCrawler():
    # base_url: str
    # base_domain: str
    # page_data: PageData
    # lock: asyncio.Lock
    # semaphore: asyncio.Semaphore
    # max_concurrency: int
    # session: aiohttp.ClientSession

    def __init__(self, base_url: str, max_concurrency: int = 10, max_pages: int = 100) -> None:

        self.base_url: str = base_url
        self.base_domain: str = urllib.parse.urlparse(base_url).netloc
        self.page_data: dict[str, PageData] = {}

        self.lock: asyncio.Lock = asyncio.Lock()
        self.max_concurrency: int = max_concurrency
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(value=self.max_concurrency)
        self.session: aiohttp.ClientSession
        self.max_pages: int = max_pages
        self.should_stop: bool = False
        self.all_tasks: set = set()
        

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url: str):
        async with self.lock:
            if self.should_stop == True:
                return False

            if normalized_url in self.page_data:
                return False

            if len(self.page_data) > self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                for task in self.all_tasks:
                    task.cancel()
                return False

            return True        
            
            
        
    async def get_html(self, url: str) -> str | None:
        headers = {'user-agent': "BootCrawler/1.0"}

        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status >= 400:
                    print(f"Client/Server error: {resp.status}")
                    return None

                if not resp.headers.get('Content-Type', '').startswith('text/html'):
                    print(f"not html: {resp.headers.get('Content-Type')}")
                    return None

                return await resp.text()
        except Exception as e:
            print(e)
            return None
        
    async def crawl_page(self, base_url: str, current_url: str | None=None):
        if self.should_stop == True:
            return

        if current_url is None:
            current_url = base_url

        if urllib.parse.urlparse(current_url).hostname != urllib.parse.urlparse(base_url).hostname:
                return

        normalized_url = normalize_url(current_url)
        
        if await self.add_page_visit(normalized_url) == False:
            return

        async with self.semaphore:
            try:
                print(f"crawling: {current_url}")
                html = await self.get_html(current_url)
            except Exception as e:
                print(f"skipping {current_url}: {e}")
                return

            
        if html is None:
            return

        
        data = extract_page_data(html, current_url)
        async with self.lock:
            self.page_data[normalized_url] = data

        urls = data['outgoing_links']

        tasks = []
        for url in urls:
            task = asyncio.create_task(self._crawl_and_cleanup(base_url, url))
            self.all_tasks.add(task)
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _crawl_and_cleanup(self, base_url: str, url: str):
        try:
            await self.crawl_page(base_url, url)
        finally:
            self.all_tasks.discard(asyncio.current_task())


    async def crawl(self) -> dict[str, PageData] | None:
        base_url = self.base_url

        await self.crawl_page(base_url)

        return self.page_data

    



async def crawl_site_async(base_url: str, max_concurrency: int = 10, max_pages: int = 100) -> dict[str, PageData] | None:

    async with AsyncCrawler(base_url, max_concurrency=max_concurrency, max_pages=max_pages) as crawler:
        await crawler.crawl()
        return crawler.page_data
   






        





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


    



