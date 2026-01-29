"""
clean_extracted_data.py

General idea (multiline summary)
This script reads raw extracted session logs (CSV-like where each line is a session:
comma-separated URL paths). It normalizes and filters each path to keep only
meaningful navigation steps for sequence/mining tasks. Cleaning steps:
- remove query strings/fragments and normalize slashes
- convert file endpoints to their parent directory (drop file extensions)
- detect and drop static/noise paths (images, css, js, cgi, etc.)
- limit path depth to avoid overly specific resource paths
- remove consecutive duplicate paths within a session
- truncate long sessions to a maximum length
- write filtered sessions that contain at least 2 meaningful steps

The code below contains inline comments that explain each line or small block.
"""

import re          # regular expressions for slash normalization
import os          # path utilities (basename, dirname)


# Paths to filter out - these are static resources or non-meaningful navigation
NOISE_PATHS = {
    '/images',
    '/icons',
    '/htbin',
    '/cgi-bin',
    '/cgi',
    '/bin',
    '/static',
    '/assets',
    '/css',
    '/js',
    '/fonts',
    '/media',
}

# Prefixes that indicate noise paths (for quick startswith checks)
NOISE_PREFIXES = (
    '/images/',
    '/icons/',
    '/cgi-bin/',
    '/htbin/',
    '/static/',
    '/assets/',
    '/css/',
    '/js/',
    '/fonts/',
    '/media/',
)

# Maximum path depth to keep (e.g., keep up to /a/b/c => depth 3)
MAX_PATH_DEPTH = 3

# Maximum session length (too long sessions add noise and make patterns sparse)
MAX_SESSION_LENGTH = 25


def is_noise_path(path):
    """
    Check if a path is a noise path that should be filtered out.
    Returns True if the path should be removed, False otherwise.
    """
    path = path.strip()                            # remove surrounding whitespace

    # Check exact matches against the NOISE_PATHS set
    if path in NOISE_PATHS:
        return True                                # exact noise path found

    # Check if the path starts with any known noise prefix
    if path.startswith(NOISE_PREFIXES):
        return True                                # path begins with a noise prefix

    # Filter out cgi-bin imagemap paths (e.g., '/cgi-bin/imagemap/countdown69,186')
    if 'imagemap' in path.lower():
        return True                                # imagemap usually not meaningful

    # Filter paths with commas (often malformed or coordinate-like)
    if ',' in path:
        return True                                # comma indicates non-navigational resource

    return False                                   # path does not match noise rules


def limit_path_depth(path, max_depth=MAX_PATH_DEPTH):
    """
    Limit path depth to avoid overly specific paths.
    Example: '/shuttle/missions/sts-69/images' -> '/shuttle/missions/sts-69'
    """
    parts = path.split('/')                         # split on slash, parts[0] == '' for leading '/'
    # If there are more segments than allowed (note +1 for the leading empty segment),
    # slice to keep only up to max_depth segments after the leading empty one.
    if len(parts) > max_depth + 1:
        return '/'.join(parts[:max_depth + 1])      # rejoin first segments to desired depth
    return path                                     # path is already within allowed depth


def clean_path(path):
    """
    Clean and normalize a URL path:
    - Remove query strings and fragments
    - Normalize multiple slashes into one
    - Strip trailing slashes (except root '/')
    - Remove file endpoints (if the last segment has an extension), keeping the directory
    Returns the cleaned path.
    """
    # Remove query string and fragment by splitting on '?' and '#'
    path = path.split('?')[0].split('#')[0]         # drop everything after '?' or '#'

    # Normalize repeated slashes into a single slash (e.g., '///a//b' -> '/a/b')
    path = re.sub(r'/+', '/', path)

    # Remove trailing slash, but keep single root '/'
    if path.endswith('/') and len(path) > 1:
        path = path[:-1]                             # drop final slash for non-root paths

    # Check basename for a file extension (a dot in the final segment)
    basename = os.path.basename(path)               # get final path segment
    if '.' in basename:
        path = os.path.dirname(path)                # path had a file, so use its parent directory

    # Strip trailing slash again because dirname may add one
    if path.endswith('/') and len(path) > 1:
        path = path[:-1]

    return path                                      # return normalized, extension-free path


def is_valid_path(path):
    """
    Check if the path is valid for session tracking.
    - Reject empty and root paths
    - Reject numeric-only paths (commonly errors or coordinates)
    - Reject very short paths (less than 3 chars after the leading '/')
    Returns True if the path is acceptable, False otherwise.
    """
    if not path or path == '/':
        return False                                 # empty or root not meaningful

    # Remove leading/trailing slashes for content checks
    stripped = path.strip('/')

    # Reject paths that consist only of digits
    if stripped.isdigit():
        return False                                 # numeric-only paths are noisy

    # Reject very short names, e.g., '/a' or '/ab' (length less than 3)
    if len(stripped) < 3:
        return False                                 # too short to be meaningful

    return True                                      # path passes basic validity checks


def remove_consecutive_duplicates(paths):
    """
    Remove consecutive duplicate paths within a session.
    Example: ['/a','/a','/b','/b','/a'] -> ['/a','/b','/a']
    This preserves non-consecutive repeats but removes repeated consecutive noise.
    """
    if not paths:
        return paths                                 # nothing to do for empty list

    result = [paths[0]]                              # always keep the first item
    for path in paths[1:]:                           # iterate from second element to end
        if path != result[-1]:                       # compare with last kept item
            result.append(path)                      # append only when different
    return result                                    # return deduped list


def main():
    """
    Main function to clean extracted log data.
    Reads from extracted_logs.csv and writes cleaned sessions to cleaned_data.csv.
    Tracks counts for reporting.
    """
    input_file = 'Data/extractedAndcleanedData/extracted_logs.csv'   # input path (raw sessions)
    output_file = 'Data/extractedAndcleanedData/cleaned_data.csv'   # output path (cleaned sessions)

    print(f"Reading from {input_file}...")             # inform user which file is used

    total_sessions = 0                                 # counter for written sessions
    total_paths = 0                                    # counter for total cleaned paths written

    try:
        # Open input for reading and output for writing (text mode)
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:                       # iterate each session line in input
                line = line.strip()                   # remove newline and surrounding whitespace
                if not line:
                    continue                          # skip empty lines entirely

                # Split the line into individual path tokens (CSV-style, comma-separated)
                paths = line.split(',')

                # Clean each path and filter out noise into a temporary list
                cleaned_paths = []                   # will store cleaned, valid, non-noise paths
                for path in paths:
                    cleaned = clean_path(path)       # normalize path (remove queries, ext, etc.)
                    # Keep the path only if it is valid and not a noise path
                    if is_valid_path(cleaned) and not is_noise_path(cleaned):
                        # Apply path depth limiting to discard too-deep segments
                        cleaned = limit_path_depth(cleaned)
                        cleaned_paths.append(cleaned) # add cleaned and depth-limited path

                # Remove consecutive duplicates (may appear after depth limiting)
                cleaned_paths = remove_consecutive_duplicates(cleaned_paths)

                # Truncate sessions that exceed the maximum allowed length
                if len(cleaned_paths) > MAX_SESSION_LENGTH:
                    cleaned_paths = cleaned_paths[:MAX_SESSION_LENGTH]  # keep only first N

                # Only keep sessions that contain at least 2 meaningful steps
                if len(cleaned_paths) >= 2:
                    outfile.write(",".join(cleaned_paths) + '\n')  # write cleaned session to file
                    total_sessions += 1                           # increment session counter
                    total_paths += len(cleaned_paths)             # accumulate paths count

        # After processing all lines, print summary stats
        print(f"Done!")
        print(f"  - Total sessions: {total_sessions}")
        print(f"  - Total paths: {total_paths}")
        if total_sessions > 0:
            print(f"  - Average paths per session: {total_paths / total_sessions:.2f}")

    except FileNotFoundError:
        # Input file missing — give actionable message to the user
        print(f"Error: {input_file} not found. Run extract_logs.py first.")


# Standard Python entrypoint guard so main() runs only when script executed directly
if __name__ == "__main__":
    main()
