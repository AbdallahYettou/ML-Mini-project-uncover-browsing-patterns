"""
extract_logs.py
Extracts raw data from NASA access log files and saves to CSV.
This file only does extraction - no cleaning or filtering.
"""

import re

def process_log_file(filename, limit=None):
    """
    Process a NASA access log file and extract raw session data.
    Returns a dictionary mapping hosts to their list of paths.
    """
    sessions = {}
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            count = 0
            for line in f:
                if limit is not None and count >= limit:
                    break
                
                # Match GET requests and extract host, path, and status
                match = re.match(r'^(\S+) .* "GET (.*?) HTTP.*" (\d{3})', line)
                
                if match:
                    host = match.group(1)
                    path = match.group(2)
                    status = int(match.group(3))
                    
                    count += 1
                    
                    # Skip error responses (4xx and 5xx)
                    if status >= 400:
                        continue
                    
                    if host not in sessions:
                        sessions[host] = []
                    sessions[host].append(path)
                    
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    return sessions


def main():
    """
    Main function to extract data from log files and save to CSV.
    """
    files = ['access_log_Aug95', 'access_log_Jul95']
    output_file = 'extracted_logs.csv'
    all_sessions = {}

    for filename in files:
        print(f"Processing {filename}...")
        file_sessions = process_log_file(filename)
        
        # Merge sessions from multiple files
        for host, paths in file_sessions.items():
            if host not in all_sessions:
                all_sessions[host] = []
            all_sessions[host].extend(paths)

    print(f"Writing raw sessions to {output_file}...")
    
    total_sessions = 0
    total_paths = 0
    
    with open(output_file, 'w') as f:
        for host, paths in all_sessions.items():
            if paths and len(paths) >= 2:
                line = ",".join(paths)
                f.write(line + '\n')
                total_sessions += 1
                total_paths += len(paths)
    
    print(f"Done!")
    print(f"  - Total sessions: {total_sessions}")
    print(f"  - Total paths: {total_paths}")
    if total_sessions > 0:
        print(f"  - Average paths per session: {total_paths / total_sessions:.2f}")


if __name__ == "__main__":
    main()
