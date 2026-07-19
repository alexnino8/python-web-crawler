import sys
from crawl import get_html

def main():

    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    
    if len(sys.argv) > 2: 
        print("too many arguments provided")
        sys.exit(1)

    website = sys.argv[1]

    print(f"starting crawl of {website}")

    print(get_html(website))


if __name__ == "__main__":
    main()
