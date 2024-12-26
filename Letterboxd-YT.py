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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

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

def init_driver():
    service = Service(executable_path="chromedriver")  # Update path
    options = webdriver.ChromeOptions()
    options.headless = False
    # Keep the same user-data-dir so cookies persist:
    options.add_argument('--user-data-dir=/tmp/chromeprofile')
    # Remove or reduce extra flags, but keep these:
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def letterboxd_login(driver: webdriver.Chrome):
    driver.get("https://letterboxd.com/sign-in/")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "field-username"))).send_keys(LETTERBOXD_USERNAME)
    driver.find_element(By.ID, "field-password").send_keys(LETTERBOXD_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "navitem")))
    print("Logged in successfully.")
    # Store cookies after successful login
    cookies = driver.get_cookies()
    return cookies

def search_movie_on_letterboxd(driver: webdriver.Chrome, movie_title, cookies):
    # Add stored cookies to maintain session
    for cookie in cookies:
        driver.add_cookie(cookie)
    
    print("Cookies added, checking login status...")
    nav_items = driver.find_elements(By.CLASS_NAME, "navitem")
    if nav_items:
        print("Still logged in", nav_items)
    else:
        print("Session lost!")

    try:
        driver.get("https://letterboxd.com/film/good/")
        watchlist_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".action.-watchlist.add-to-watchlist.ajax-click-action"))
        )
        watchlist_button.click()
        sleep(100)
        # Click search icon
        # print("Clicking search icon...")
        # search_button = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".main-nav>.navitems>.navitem.-search a"))
        # )
        # search_button.click()
        # print("Search icon clicked")
        
        # # Enter movie title in search box
        # driver.find_element(By.ID, "search-q").send_keys(movie_title)
        # # search_input.send_keys(Keys.RETURN)
        # print("Movie title entered")

        # enterSearch = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-form .action"))
        # )
        # enterSearch.click()
        # print("Search results loaded")
        
        # # Wait for results
        # filmPoster = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "h2 .film-title-wrapper a"))
        # )
        # filmPoster.click()
        # print("Movie page loaded")

        # watchList = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, "action -watchlist add-to-watchlist ajax-click-action"))
        # )
        # watchList.click()
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    driver = init_driver()
    cookies = letterboxd_login(driver)
    search_movie_on_letterboxd(driver, "Good", cookies)