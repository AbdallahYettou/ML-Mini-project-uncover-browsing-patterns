"""
process_logs.py

General idea (multiline summary)
This small script parses an Apache-style access log file and extracts user
sessions keyed by the requesting host (remote host or hostname). For each GET
request it captures the requested path if the response status code indicates
success (< 400). It then writes sessions containing at least two requests into
a CSV-like file where each line is a comma-separated sequence of paths for one
host. The script supports an optional limit on how many log lines to process.

Files / functions
- process_log_file(filename, limit=None): read the log file and return a dict
  mapping host -> list of paths (in chronological order, as seen in the file).
- main(): driver that calls process_log_file for specified files, merges
  results, and writes `extracted_logs.csv` with only sessions that have >= 2 paths.
"""

import re


def process_log_file(filename, limit=None):
    """
    Read `filename` (an access log) and return sessions grouped by host.

    Parameters
    - filename: path to the log file (text)
    - limit: optional integer to stop after processing `limit` matched lines

    Returns
    - sessions: dict mapping host (str) -> list of path strings in order seen
    """
    sessions = {}                      # will hold host -> list_of_paths

    try:
        # Open using utf-8 and ignore errors to be resilient to odd characters
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            count = 0                  # count of processed GET lines (respects `limit`)
            for line in f:             # iterate over each line in the file
                # If a limit was provided and we've already processed that many GETs, stop
                if limit is not None and count >= limit:
                    break

                # Use a regex to match lines with GET requests and capture:
                #  group(1) -> host (first non-space sequence)
                #  group(2) -> requested path (the part between GET and HTTP)
                #  group(3) -> status code (three digits after the request)
                #
                # Example log fragment:
                # johnsonj2.mayo.edu - - [26/Aug/1995:01:36:45 -0400] "GET /facilities/lc39a.html HTTP/1.0" 200 7008
                match = re.match(r'^(\S+) .* "GET (.*?) HTTP.*" (\d{3})', line)

                # If the regex matches, extract host, path and status
                if match:
                    host = match.group(1)         # the remote host or hostname
                    path = match.group(2)         # the requested path, e.g. /images/foo.gif
                    status = int(match.group(3))  # numeric HTTP status, e.g. 200

                    count += 1                    # count this matched GET line

                    # Skip error responses: treat 4xx and 5xx as not part of successful navigation
                    if status >= 400:
                        continue                  # ignore this request and continue scanning

                    # Ensure the host key exists in the sessions dict
                    if host not in sessions:
                        sessions[host] = []      # initialize an empty list for this host

                    # Append the path for this host in the order encountered
                    sessions[host].append(path)

    except FileNotFoundError:
        # If the file is missing, print an informative message and return empty sessions
        print(f"Error: File {filename} not found.")

    # Return the mapping host -> list(paths)
    return sessions


def main():
    """
    Driver function:
    - defines the list of log files to process
    - calls process_log_file on each file
    - merges sessions across files
    - writes sessions of length >= 2 to output CSV-like file
    - prints summary statistics
    """
    # List of input files to process. You can add multiple files here to merge sessions.
    files = ['Data/Logs/access_log_Aug95']  # fixed entry (no duplicate)
    output_file = 'Data/extractedAndcleanedData/extracted_logs.csv'
    all_sessions = {}                         # will hold merged sessions across files

    # Process each file in the list
    for filename in files:
        print(f"Processing {filename}...")
        file_sessions = process_log_file(filename)  # parse and get host->paths for this file

        # Merge sessions from this file into the global all_sessions dict
        for host, paths in file_sessions.items():
            if host not in all_sessions:
                all_sessions[host] = []        # initialize if this host not seen before
            # extend keeps chronological ordering (paths appended in the order they were read)
            all_sessions[host].extend(paths)

    print(f"Writing raw sessions to {output_file}...")

    total_sessions = 0
    total_paths = 0

    # Write only sessions that contain at least two paths (useful for session sequence mining)
    with open(output_file, 'w', encoding='utf-8') as f:
        for host, paths in all_sessions.items():
            # Keep only non-empty sessions and those with at least 2 requests
            if paths and len(paths) >= 2:
                line = ",".join(paths)  # produce a CSV-like comma separated sequence of paths
                f.write(line + '\n')    # write one session per line
                total_sessions += 1
                total_paths += len(paths)

    # Print a small summary with counts
    print(f"Done!")
    print(f"  - Total sessions: {total_sessions}")
    print(f"  - Total paths: {total_paths}")
    if total_sessions > 0:
        print(f"  - Average paths per session: {total_paths / total_sessions:.2f}")


# Standard Python guard so main() runs only when this file is executed directly
if __name__ == "__main__":
    main()
