"""
clean_extracted_data.py
Cleans extracted log data by:
- Removing file extensions (keeping only directories)
- Removing query strings and fragments
- Normalizing paths
- Removing noise paths like /images, /icons, /htbin
- Removing consecutive duplicates
"""

import re
import os


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

# Path prefixes to filter out
NOISE_PREFIXES = [
    '/images/',
    '/icons/',
    '/htbin/',
    '/cgi-bin/',
    '/cgi/',
    '/static/',
    '/assets/',
    '/css/',
    '/js/',
    '/fonts/',
    '/media/',
]


def is_noise_path(path):
    """
    Check if a path is a noise path that should be filtered out.
    """
    path = path.strip()
    
    # Check exact matches
    if path in NOISE_PATHS:
        return True
    
    # Check prefixes
    for prefix in NOISE_PREFIXES:
        if path.startswith(prefix):
            return True
    
    return False


def clean_path(path):
    """
    Clean and normalize a URL path:
    - Remove file extensions (keep only directory)
    - Strip trailing slashes
    - Remove query strings and fragments
    - Normalize multiple slashes
    """
    # Remove query strings and fragments
    path = path.split('?')[0].split('#')[0]
    
    # Normalize multiple slashes to single slash
    path = re.sub(r'/+', '/', path)
    
    # Strip trailing slash
    if path.endswith('/') and len(path) > 1:
        path = path[:-1]
    
    # Check if basename has an extension (contains a dot)
    basename = os.path.basename(path)
    if '.' in basename:
        path = os.path.dirname(path)
        
    # Strip trailing slash again after dirname
    if path.endswith('/') and len(path) > 1:
        path = path[:-1]

    return path


def is_valid_path(path):
    """
    Check if the path is valid for session tracking.
    Filters out paths that don't represent meaningful navigation.
    """
    if not path or path == '/':
        return False
    
    return True


def remove_consecutive_duplicates(paths):
    """
    Remove consecutive duplicate paths within a session.
    """
    if not paths:
        return paths
    
    result = [paths[0]]
    for path in paths[1:]:
        if path != result[-1]:
            result.append(path)
    return result


def main():
    """
    Main function to clean extracted log data.
    Reads from extracted_logs.csv and writes to cleaned_data.csv
    """
    input_file = 'extracted_logs.csv'
    output_file = 'cleaned_data.csv'
    
    print(f"Reading from {input_file}...")
    
    total_sessions = 0
    total_paths = 0
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                
                # Split the line into paths
                paths = line.split(',')
                
                # Clean each path and filter out noise
                cleaned_paths = []
                for path in paths:
                    cleaned = clean_path(path)
                    if is_valid_path(cleaned) and not is_noise_path(cleaned):
                        cleaned_paths.append(cleaned)
                
                # Remove consecutive duplicates
                cleaned_paths = remove_consecutive_duplicates(cleaned_paths)
                
                # Only keep sessions with at least 2 paths
                if len(cleaned_paths) >= 2:
                    outfile.write(",".join(cleaned_paths) + '\n')
                    total_sessions += 1
                    total_paths += len(cleaned_paths)
        
        print(f"Done!")
        print(f"  - Total sessions: {total_sessions}")
        print(f"  - Total paths: {total_paths}")
        if total_sessions > 0:
            print(f"  - Average paths per session: {total_paths / total_sessions:.2f}")
            
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Run extract_logs.py first.")


if __name__ == "__main__":
    main()
