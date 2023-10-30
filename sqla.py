#!/usr/bin/env python3

import subprocess
import signal
import sys
import threading
import queue
import tempfile
import os

# Constants
NUM_THREADS = 25
BATCH_SIZE = 5

# Queue to hold batches of URLs
url_queue = queue.Queue()

def signal_handler(sig, frame):
    """ Handle Ctrl+C and gracefully exit """
    sys.exit(0)

def execute_batch(command, batch, command_args, output_file):
    """ Execute the command on a batch of URLs, save and display the output. """
    # Create a temporary file to hold the batch of URLs
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
        tmp_file_name = tmp_file.name
        for url in batch:
            tmp_file.write(url + '\n')

    full_command = f"{command} {tmp_file_name} {command_args}"
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
    """ Worker thread function to process batches of URLs. """
    while True:
        batch = url_queue.get()
        if batch is None:
            break
        execute_batch(command, batch, command_args, output_file)
        url_queue.task_done()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: ./script_name.py 'command' -o output_file.txt -i input_arguments_file.txt")
        sys.exit(1)

    command = sys.argv[1]
    output_file_flag = sys.argv[2]
    output_file = sys.argv[3]
    input_args_flag = sys.argv[4]
    input_args_file = sys.argv[5]

    # Ensure output option is specified correctly
    if output_file_flag != "-o":
        print("Error: Output file must be specified with -o option")
        sys.exit(1)

    # Ensure input arguments file option is specified correctly
    if input_args_flag != "-i":
        print("Error: Input arguments file must be specified with -i option")
        sys.exit(1)

    # Read command arguments from the specified file
    with open(input_args_file, 'r') as f:
        command_args = f.read().strip()

    # Register the Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start worker threads
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(command, command_args, output_file))
        t.start()
        threads.append(t)

    # Read URLs from stdin and enqueue batches
    batch = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            batch.append(line)
            if len(batch) == BATCH_SIZE:
                url_queue.put(batch)
                batch = []
    if batch:
        url_queue.put(batch)

    # Block until all URLs are processed
    url_queue.join()

    # Stop worker threads
    for _ in range(NUM_THREADS):
        url_queue.put(None)
    for t in threads:
        t.join()

