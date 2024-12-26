import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fuzzywuzzy import fuzz
from urllib.parse import urlencode
from movie_name_extractor import extract_movie_name
from bs4 import BeautifulSoup
from time import sleep
from dotenv import load_dotenv
import time

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

def login_to_letterboxd():
    session = requests.Session()
    login_url = "https://letterboxd.com/"

    # Step 1: Get the login page to extract CSRF token
    login_page = session.get(login_url)
    if login_page.status_code != 200:
        print("Failed to load login page.")
        return None

    soup = BeautifulSoup(login_page.text, "lxml")
    csrf_input = soup.find("input", {"name": "__csrf"})
    if not csrf_input:
        print("CSRF token not found on login page.")
        return None
    csrf_token = csrf_input.get("value")

    # Step 2: Prepare payload with CSRF token
    payload = {
        "__csrf": csrf_token,
        "username": LETTERBOXD_USERNAME,
        "password": LETTERBOXD_PASSWORD
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": login_url
    }

    # Step 3: Post login data
    resp = session.post(login_url, data=payload, headers=headers)
    if resp.status_code != 200 and resp.status_code != 302:
        print(f"Login failed with status code: {resp.status_code}")
        return None

    # Step 4: Verify login by checking a known authenticated page
    profile_url = "https://letterboxd.com/bhavyaprobably/"
    profile_resp = session.get(profile_url, headers=headers)
    if LETTERBOXD_USERNAME.lower() in profile_resp.text.lower():
        print("Login successful.")
        return session
    else:
        print("Login verification failed.")
        return None

def search_movie_on_letterboxd(movie_title):
    # searches a movie on letterboxd, and finds the result url/s
    # we can just take the first result only too

def add_to_watchlist(session, film_link):
    # adds a movie to the watchlist on letterboxd
    watchlist_url = "https://letterboxd.com" + film_link + "add-to-watchlist/"
    session.post(watchlist_url)
    return True

if __name__ == "__main__":
    session = login_to_letterboxd()
    playlist_id = "PL0PE6lZEhm7uaRpotx_urp319V_OsJdq7"
    videos = get_new_videos_from_playlist(playlist_id)
    # for video in videos:
    movie_title = extract_movie_name(videos[0])
    results = search_movie_on_letterboxd('Good')
    print(f"Search results for '{movie_title}': {results}")