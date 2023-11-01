import argparse
import re

# ANSI color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'reset': '\033[0m'
}

def extract_urls(file_path):
    urls = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.rstrip('\n')
            match = re.search(r'http[s]?://[^ ]+', line)
            if match:
                url = match.group()
                ip = url.split('/')[2]  # Extract the IP/domain from the URL
                urls[ip] = url
    return urls

def colorize(text, color):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

def merge_files(attack_surface_path, found_file_path, output_path=None, colorize_output=False):
    urls = extract_urls(found_file_path)
    results = []
    
    with open(attack_surface_path, 'r') as attack_surface:
        for line in attack_surface:
            line = line.rstrip('\n')
            parts = line.split(':')
            if len(parts) == 2:
                domain, ip = parts
                extracted_url = urls.get(ip)
                if extracted_url:
                    if colorize_output:
                        domain = colorize(domain, 'green')
                        ip = colorize(ip, 'yellow')
                        extracted_url = colorize(extracted_url, 'red')
                    result_line = f'{domain}:{ip}:{extracted_url}\n'
                    results.append(result_line)
                    if not output_path:
                        print(result_line, end='')

    if output_path:
        with open(output_path, 'w') as output_file:
            output_file.writelines(results)

def main():
    parser = argparse.ArgumentParser(description='Merge URLs into attack surface file.')
    parser.add_argument('--attack_surface', required=True, help='Path to the attack surface file')
    parser.add_argument('--found', required=True, help='Path to the file with found URLs')
    parser.add_argument('--output', help='Optional path to the output file')
    parser.add_argument('--color', action='store_true', help='Enable colorized output')
    
    args = parser.parse_args()
    
    merge_files(args.attack_surface, args.found, args.output, args.color)

if __name__ == '__main__':
    main()

