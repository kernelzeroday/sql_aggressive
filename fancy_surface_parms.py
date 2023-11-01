import argparse
import re

# ANSI color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'reset': '\033[0m'
}

def colorize(text, color):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

def debug_print(debug, message):
    if debug:
        print(f"Debug: {message}")

def parse_url_line(line):
    match = re.search(r'http[s]?://[^ ]+', line)
    return match.group() if match else None

def parse_parameter_line(line):
    param_match = re.search(r'Parameter: (\w+) \(GET\)', line)
    return param_match.group(1) if param_match else None

def read_file_lines(file_path):
    with open(file_path, 'r') as file:
        return [line.rstrip('\n') for line in file]

def extract_urls(file_lines, debug):
    urls = {}
    for line in file_lines:
        url = parse_url_line(line)
        if url:
            ip = url.split('/')[2]
            urls[ip] = url
            debug_print(debug, f"Found URL - {url}")
    return urls

def parse_additional_info(file_lines, colorize_output, debug):
    url_params = {}
    current_url = None
    for i, line in enumerate(file_lines):
        if 'http' in line:
            current_url = parse_url_line(line)
            if current_url:
                url_params[current_url] = []
        elif current_url:
            param = parse_parameter_line(line)
            if param:
                types = []
                j = i + 1
                while j < len(file_lines) and 'Type:' in file_lines[j]:
                    types.append(file_lines[j].split(': ')[1])
                    j += 1
                result = f"[ param={param}, type={' '.join(types)} ]"
                if colorize_output:
                    result = colorize(result, 'blue')
                url_params[current_url].append(result)
                debug_print(debug, f"Found param - {result}")
    return url_params
def merge_results(attack_surface_lines, urls, url_params, colorize_output, debug):
    results = []
    for line in attack_surface_lines:
        parts = line.split(':')
        if len(parts) == 2:
            domain, ip = parts
            for extracted_url, params in url_params.items():
                if ip in extracted_url or domain in extracted_url:
                    if colorize_output:
                        domain = colorize(domain, 'green')
                        ip = colorize(ip, 'yellow')
                        extracted_url = colorize(extracted_url, 'red')
                    result_line = f'{domain}:{ip}:{extracted_url}'
                    param_details = '    '.join(params)
                    if param_details:
                        result_line += f'    {param_details}'
                    result_line += '\n'
                    results.append(result_line)
                    debug_print(debug, f"Matched {domain}:{ip} with {extracted_url}")
                    break
    return results

def main():
    parser = argparse.ArgumentParser(description='Merge URLs into attack surface file.')
    parser.add_argument('--attack_surface', required=True, help='Path to the attack surface file')
    parser.add_argument('--found', required=True, help='Path to the file with found URLs')
    parser.add_argument('--output', help='Optional path to the output file')
    parser.add_argument('--color', action='store_true', help='Enable colorized output')
    parser.add_argument('--parse_found', action='store_true', help='Parse additional information from found file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    try:
        attack_surface_lines = read_file_lines(args.attack_surface)
        found_file_lines = read_file_lines(args.found)
        
        urls = extract_urls(found_file_lines, args.debug)
        url_params = parse_additional_info(found_file_lines, args.color, args.debug) if args.parse_found else {}

        results = merge_results(attack_surface_lines, urls, url_params, args.color, args.debug)

        if args.output:
            with open(args.output, 'w') as output_file:
                output_file.writelines(results)
        else:
            for result in results:
                print(result, end='')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()

