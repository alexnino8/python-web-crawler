import sys
import asyncio
from crawl import crawl_site_async

async def main_async():

    if len(sys.argv) < 2:
        print("usage: main.py URL [max_concurrency] [max_pages]")
        sys.exit(1)

    if len(sys.argv) > 4: 
            print("too many arguments provided")
            sys.exit(1)

    base_url = sys.argv[1]
    try:
        max_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    except ValueError:
        print("usage: main.py URL [max_concurrency] [max_pages]")
        sys.exit(1)
    

    print(f"starting crawl of {base_url}")

    page_data = await crawl_site_async(base_url, max_concurrency=max_concurrency, max_pages=max_pages)
    if page_data is None:
        print("no page data")
        sys.exit(1)

    print(f"Found {len(page_data)} pages")
    for page in page_data.values():
        print(page)






if __name__ == "__main__":
    asyncio.run(main_async())
