import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fuzzywuzzy import fuzz
from urllib.parse import urlencode
from movie_name_extractor import extract_movie_name
from notion_client import Client
import time
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

if not (YOUTUBE_API_KEY and NOTION_TOKEN and NOTION_PAGE_ID):
    raise ValueError("Missing credentials in environment variables.")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
notion = Client(auth=NOTION_TOKEN)

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

# 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

def update_notion_page(movie_title):
    notion.pages.create(
        parent={"page_id": NOTION_PAGE_ID},
        properties={
            "title": {
                "title": [
                    {
                        "text": {
                            "content": movie_title
                        }
                    }
                ]
            }
        }
    )

if __name__ == "__main__":
    playlist_id = "PL0PE6lZEhm7uaRpotx_urp319V_OsJdq7"
    seen_videos = set()

    while True:
        videos = get_new_videos_from_playlist(playlist_id)
        for video in videos:
            if video not in seen_videos:
                movie_title = extract_movie_name(video)
                print(f"Extracted movie title: {movie_title}")
                update_notion_page(movie_title)
                seen_videos.add(video)
        time.sleep(60)