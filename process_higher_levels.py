import sys
import re
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process logs and find URLs with potential injection points.')
    parser.add_argument('--found', help='File containing already found URLs to be excluded from the output.', type=str)
    return parser.parse_args()

def main():
    args = parse_arguments()

    # Load previously found URLs if provided
    found_urls = set()
    if args.found:
        with open(args.found, 'r') as f:
            for line in f:
                found_urls.add(line.strip())

    lines = sys.stdin.readlines()
    for i, line in enumerate(lines):
        if "heuristic (basic) test shows that GET parameter" in line:
            # Find the corresponding URL
            url_line = ""
            for j in range(i, max(i - 150, -1), -1):
                if re.match(r"\[\d+/\d+\] URL:", lines[j]):
                    url_line = lines[j + 1].replace("GET ", "").strip()  # Remove "GET"
                    break

            # Print URL if it's not in the found_urls set
            if url_line and url_line not in found_urls:
                print(url_line)

if __name__ == "__main__":
    main()

