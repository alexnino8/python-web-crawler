import sys
from crawl import get_html, crawl_page

def main():

    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    
    if len(sys.argv) > 2: 
        print("too many arguments provided")
        sys.exit(1)

    base_url = sys.argv[1]
    page_data = {}
    

    print(f"starting crawl of {base_url}")

    crawl_page(base_url, page_data=page_data)

    print(f"Found {len(page_data)} pages")
    for url, data in page_data.items():
        print(f"{url}: {data}")




if __name__ == "__main__":
    main()
