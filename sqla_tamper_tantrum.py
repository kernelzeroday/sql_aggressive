#!/usr/bin/env python3

import subprocess
import signal
import sys
import threading
import queue
import tempfile
import os
import random

# Constants
NUM_THREADS = 25
BATCH_SIZE = 5

# Queue to hold batches of URLs with tamper scripts
url_queue = queue.Queue()

# List to hold tamper scripts
tamper_scripts = []

def signal_handler(sig, frame):
    """ Handle Ctrl+C and gracefully exit """
    sys.exit(0)

def execute_command(command, url, tamper_script, command_args, output_file):
    """ Execute the command on a single URL with a given tamper script, save and display the output. """
    # Create a temporary file to hold the URL
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
        tmp_file_name = tmp_file.name
        tmp_file.write(url + '\n')

    full_command = f"{command} {tmp_file_name} --tamper={tamper_script} {command_args}"
    try:
        print(f"Executing command: {full_command}")
        result = subprocess.run(
            full_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        output = result.stdout.decode()

        # Print to terminal
        print(output)

        # Write to output file
        with open(output_file, "a") as f:
            f.write(f"Command: {full_command}\n")
            f.write(output)
            f.write("\n")
    except Exception as e:
        error_msg = f"Error executing command: {full_command}\nError: {str(e)}\n"
        print(error_msg)
        with open(output_file, "a") as f:
            f.write(error_msg)
    finally:
        # Remove the temporary file
        os.remove(tmp_file_name)

def worker(command, command_args, output_file):
    """ Worker thread function to process URLs with tamper scripts. """
    while True:
        task = url_queue.get()
        if task is None:
            break

        url, tamper_script = task
        execute_command(command, url, tamper_script, command_args, output_file)
        url_queue.task_done()

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: ./script_name.py 'command' -o output_file.txt -i input_arguments_file.txt -t tampers_file.txt")
        sys.exit(1)

    command = sys.argv[1]
    output_file_flag = sys.argv[2]
    output_file = sys.argv[3]
    input_args_flag = sys.argv[4]
    input_args_file = sys.argv[5]
    tampers_flag = sys.argv[6]
    tampers_file = sys.argv[7]

    # Ensure options are specified correctly
    if output_file_flag != "-o" or input_args_flag != "-i" or tampers_flag != "-t":
        print("Error: Output file must be specified with -o, input arguments file with -i, and tampers file with -t")
        sys.exit(1)

    # Read command arguments from the specified file
    with open(input_args_file, 'r') as f:
        command_args = f.read().strip()

    # Read tamper scripts from the specified file
    with open(tampers_file, 'r') as f:
        tamper_scripts = [line.strip() for line in f if line.strip()]

    # Register the Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start worker threads
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(command, command_args, output_file))
        t.start()
        threads.append(t)

    # Read URLs from stdin, shuffle them, and enqueue each URL with each tamper script
    urls = [line.strip() for line in sys.stdin if line.strip()]
    random.shuffle(urls)

    for url in urls:
        for tamper_script in tamper_scripts:
            url_queue.put((url, tamper_script))

    # Block until all tasks are processed
    url_queue.join()

    # Stop worker threads
    for _ in range(NUM_THREADS):
        url_queue.put(None)
    for t in threads:
        t.join()

