#!/usr/bin/env python3

import subprocess
import signal
import sys
import threading
import queue

# Constants
NUM_THREADS = 25
BATCH_SIZE = 5

# Queue to hold batches of URLs
url_queue = queue.Queue()

def signal_handler(sig, frame):
    """ Handle Ctrl+C and gracefully exit """
    sys.exit(0)

def execute_batch(command, batch, command_args, output_file):
    """ Execute the command on a batch of URLs and save the output. """
    for url in batch:
        full_command = f"{command} {url} {command_args}"
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            with open(output_file, "a") as f:
                f.write(f"Command: {full_command}\n")
                f.write(result.stdout.decode())
                f.write("\n")
        except Exception as e:
            with open(output_file, "a") as f:
                f.write(f"Error executing command: {full_command}\n")
                f.write(f"Error: {str(e)}\n")

def worker(command, command_args, output_file):
    """ Worker thread function to process batches of URLs. """
    while True:
        batch = url_queue.get()
        if batch is None:
            break
        execute_batch(command, batch, command_args, output_file)
        url_queue.task_done()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: ./script_name.py command -o output_file.txt -i input_arguments_file.txt")
        sys.exit(1)

    command = sys.argv[1]
    output_file = sys.argv[2]
    input_args_file = sys.argv[4]

    # Ensure output option is specified correctly
    if output_file[:2] != "-o":
        print("Error: Output file must be specified with -o option")
        sys.exit(1)
    output_file = output_file[3:]  # Remove the '-o' part

    # Ensure input arguments file option is specified correctly
    if input_args_file[:2] != "-i":
        print("Error: Input arguments file must be specified with -i option")
        sys.exit(1)
    input_args_file = input_args_file[3:]  # Remove the '-i' part

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

    print("Processing complete.")

