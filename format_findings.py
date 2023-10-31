import sys
import re

def main():
    # ANSI color codes
    URL_COLOR = '\033[94m'  # Blue
    DETAILS_COLOR = '\033[92m'  # Green
    RESET_COLOR = '\033[0m'  # Reset to default color

    lines = sys.stdin.readlines()
    for i, line in enumerate(lines):
        if "sqlmap identified the following injection point" in line:
            # Find the corresponding URL
            url_line = ""
            for j in range(i, max(i - 150, -1), -1):
                if re.match(r"\[\d+/\d+\] URL:", lines[j]):
                    url_line = lines[j + 1].strip()
                    break

            # Find the details between the "---"
            details_start, details_end = -1, -1
            for k in range(i, len(lines)):
                if "---" in lines[k]:
                    if details_start == -1:
                        details_start = k + 1
                    else:
                        details_end = k
                        break
            
            details = "".join(lines[details_start:details_end]).strip() if details_start != -1 and details_end != -1 else ""

            # Print URL and details
            if url_line and details:
                print(f"{URL_COLOR}{url_line}{RESET_COLOR}")
                print(f"{DETAILS_COLOR}{details}{RESET_COLOR}\n")

if __name__ == "__main__":
    main()

