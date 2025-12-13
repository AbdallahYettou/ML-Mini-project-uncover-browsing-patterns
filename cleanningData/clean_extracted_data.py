"""
clean_extracted_data.py
Cleans extracted log data by:
- Removing file extensions (keeping only directories)
- Removing query strings and fragments
- Normalizing paths
- Removing noise paths like /images, /icons, /htbin, /cgi-bin
- Limiting path depth to avoid overly specific paths
- Removing consecutive duplicates
- Limiting session length for cleaner patterns
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

# Prefixes that indicate noise paths
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

# Maximum path depth to keep (e.g., /shuttle/missions/sts-69 = depth 3)
MAX_PATH_DEPTH = 3

# Maximum session length (too long sessions add noise)
MAX_SESSION_LENGTH = 25


def is_noise_path(path):
    """
    Check if a path is a noise path that should be filtered out.
    """
    path = path.strip()
    
    # Check exact matches
    if path in NOISE_PATHS:
        return True
    
    # Check prefixes
    if path.startswith(NOISE_PREFIXES):
        return True
    
    # Filter out cgi-bin imagemap paths (e.g., /cgi-bin/imagemap/countdown69,186)
    if 'imagemap' in path.lower():
        return True
    
    # Filter paths with commas (usually malformed or coordinates)
    if ',' in path:
        return True
    
    return False


def limit_path_depth(path, max_depth=MAX_PATH_DEPTH):
    """
    Limit path depth to avoid overly specific paths.
    E.g., /shuttle/missions/sts-69/images → /shuttle/missions/sts-69
    """
    parts = path.split('/')
    # parts[0] will be empty string for paths starting with /
    if len(parts) > max_depth + 1:
        return '/'.join(parts[:max_depth + 1])
    return path


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
    
    # Filter out paths that are just numbers (usually errors or coordinates)
    if path.strip('/').isdigit():
        return False
    
    # Filter out very short paths (less than 3 chars after /)
    if len(path.strip('/')) < 3:
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
    input_file = 'Data/extractedAndcleanedData/extracted_logs.csv'
    output_file = 'Data/extractedAndcleanedData/cleaned_data.csv'
    
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
                        # Apply path depth limiting
                        cleaned = limit_path_depth(cleaned)
                        cleaned_paths.append(cleaned)
                
                # Remove consecutive duplicates (after depth limiting, more may become duplicates)
                cleaned_paths = remove_consecutive_duplicates(cleaned_paths)
                
                # Limit session length to avoid overly long sessions
                if len(cleaned_paths) > MAX_SESSION_LENGTH:
                    cleaned_paths = cleaned_paths[:MAX_SESSION_LENGTH]
                
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

