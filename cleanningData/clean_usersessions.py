"""
clean_usersessions.py
Cleans usersessions.csv by removing non-meaningful paths like:
- /images
- /icons  
- /htbin
- /cgi-bin
- And other static resource paths

This creates a cleaner dataset for association rule mining.
"""


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


def clean_session(session_line):
    """
    Clean a single session by removing noise paths.
    Returns cleaned paths or None if session becomes invalid.
    """
    paths = session_line.strip().split(',')
    
    # Filter out noise paths
    cleaned_paths = [p.strip() for p in paths if p.strip() and not is_noise_path(p.strip())]
    
    # Remove empty strings and paths that are just "/"
    cleaned_paths = [p for p in cleaned_paths if p and p != '/']
    
    # Remove consecutive duplicates
    cleaned_paths = remove_consecutive_duplicates(cleaned_paths)
    
    # Return None if session has less than 2 meaningful paths
    if len(cleaned_paths) < 2:
        return None
    
    return cleaned_paths


def main():
    """
    Main function to clean usersessions.csv
    """
    input_file = 'usersessions.csv'
    output_file = 'usersessions_cleaned.csv'
    
    print(f"Cleaning {input_file}...")
    print(f"Removing paths: {NOISE_PATHS}")
    
    total_original = 0
    total_cleaned = 0
    total_paths_before = 0
    total_paths_after = 0
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                line = line.strip()
                if not line or line == '""':
                    continue
                
                total_original += 1
                total_paths_before += len(line.split(','))
                
                cleaned_paths = clean_session(line)
                
                if cleaned_paths:
                    outfile.write(",".join(cleaned_paths) + '\n')
                    total_cleaned += 1
                    total_paths_after += len(cleaned_paths)
        
        print(f"\nDone! Output saved to {output_file}")
        print(f"\n--- Statistics ---")
        print(f"  Original sessions: {total_original}")
        print(f"  Cleaned sessions: {total_cleaned}")
        print(f"  Sessions removed: {total_original - total_cleaned}")
        print(f"  Original paths: {total_paths_before}")
        print(f"  Cleaned paths: {total_paths_after}")
        print(f"  Paths removed: {total_paths_before - total_paths_after}")
        
        if total_cleaned > 0:
            print(f"  Avg paths per session (before): {total_paths_before / total_original:.2f}")
            print(f"  Avg paths per session (after): {total_paths_after / total_cleaned:.2f}")
            
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")


if __name__ == "__main__":
    main()
