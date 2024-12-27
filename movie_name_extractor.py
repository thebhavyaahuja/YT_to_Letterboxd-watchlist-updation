import re

def extract_movie_name(title):
    # Step 1: Remove common trailer phrases and extra details
    title = re.sub(r'(Official Trailer.*|Trailer.*|Movie HD.*|HD.*|FULL MOVIE.*)', '', title, flags=re.IGNORECASE)

    # Step 2: Remove content in parentheses or brackets (e.g., "(2013)")
    title = re.sub(r'\(.*?\)', '', title)
    title = re.sub(r'\[.*?\]', '', title)

    # Step 3: Split by common delimiters like "-" and take the first part
    title = title.split('-')[0]
    title = title.split('|')[0]

    # Step 4: Strip leading/trailing whitespace
    title = title.strip()

    return title

