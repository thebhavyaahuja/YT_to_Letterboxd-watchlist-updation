import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlencode
from movie_name_extractor import extract_movie_name
from bs4 import BeautifulSoup
from time import sleep
from dotenv import load_dotenv
import time
import re
import json
from datetime import datetime 

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
LETTERBOXD_USERNAME = os.getenv("LETTERBOXD_USERNAME")
LETTERBOXD_PASSWORD = os.getenv("LETTERBOXD_PASSWORD")

if not (YOUTUBE_API_KEY and LETTERBOXD_USERNAME and LETTERBOXD_PASSWORD):
    raise ValueError("Missing credentials in environment variables.")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_new_videos_from_playlist(playlist_id):
    try:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()
        video_titles = []
        for item in response.get("items", []):
            title = item["snippet"]["title"]
            video_titles.append(title)
        return video_titles
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []

def get_csrf_token(html_content):
    # First, let's see what we're working with
    print("Looking for CSRF token in HTML...")

    if '__csrf' in html_content:
        print("Found '__csrf' in the content")
    if 'csrf' in html_content.lower():
        print("Found 'csrf' in the content")

    # Try to find any pattern that looks like a CSRF token
    patterns = [
        r'name="__csrf" value="([^"]+)"',
        r'data-csrf="([^"]+)"',
        r'"csrf":"([^"]+)"',
        r'supermodelCSRF = \'(\w+)',
        r'csrfToken\s*=\s*["\']([^"\']+)["\']',
        r'<input[^>]+name="__csrf"[^>]+value="([^"]+)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match and match.group(1) != "placeholder":
            return match.group(1)

    # If we couldn't find it, let's save the HTML for inspection
    with open('login_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    raise ValueError("Could not find CSRF token. HTML saved to login_page.html")

def add_to_letterboxd_watchlist(movie_title):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://letterboxd.com",
        "Referer": "https://letterboxd.com/sign-in/"
    }

    try:
        # Get login page first
        login_page = session.get("https://letterboxd.com/sign-in/", headers=headers)
        login_page.raise_for_status()

        csrf_token = get_csrf_token(login_page.text)
        print(f"Found CSRF token: {csrf_token}")

        # Prepare login data
        login_data = {
            "__csrf": csrf_token,
            "authenticationCode": "",
            "username": "bhavyaprobably",
            "password": os.getenv("LETTERBOXD_PASSWORD"),
            "remember": "true",
            "gRecaptchaAction": "signin",
            # You'll need to implement reCAPTCHA handling here
            "gRecaptchaResponse": "03AFcWeA..." # This needs to be generated
        }

        # Perform login
        login_response = session.post(
            "https://letterboxd.com/user/login.do",
            data=login_data,
            headers=headers
        )

        print("Login response status:", login_response.status_code)
        print("Login cookies:", dict(session.cookies))

        print("Login successful!")

        # Continue with watchlist addition...
        movie_page = session.get(f"https://letterboxd.com/film/{movie_title.lower().replace(' ', '-')}/")
        new_csrf_token = get_csrf_token(movie_page.text)

        watchlist_url = f"https://letterboxd.com/film/{movie_title.lower().replace(' ', '-')}/add-to-watchlist/"
        headers["X-CSRF-Token"] = new_csrf_token

        watchlist_data = {
            "__csrf": new_csrf_token
        }

        response = session.post(
            watchlist_url,
            headers=headers,
            data=watchlist_data
        )

        print("Watchlist response:", response.text)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def load_processed_videos():
    try:
        with open('processed_videos.json', 'r') as f:
            return json.load(f)
        # print("Loaded processed videos")
    except FileNotFoundError:
        return []

def save_processed_videos(videos):
    with open('processed_videos.json', 'w') as f:
        json.dump(videos, f)

def sync_new_videos():
    processed_videos = load_processed_videos()
    playlist_id = "PL0PE6lZEhm7uaRpotx_urp319V_OsJdq7"
    
    # Get current playlist videos
    current_videos = get_new_videos_from_playlist(playlist_id)
    
    # Find new videos
    new_videos = [video for video in current_videos if video not in processed_videos]
    print(new_videos)
    
    if new_videos:
        print(f"Found {len(new_videos)} new videos")
        for video in new_videos:
            movie_title = extract_movie_name(video)
            add_to_letterboxd_watchlist(movie_title)
            processed_videos.append(video)
        
        # Save updated state
        save_processed_videos(processed_videos)
    else:
        print("No new videos found")

if __name__ == "__main__":
    # print(actual_videos)
    sync_new_videos()
