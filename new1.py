import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
import requests
import re

def add_to_letterboxd_watchlist():
    # Create a session
    session = requests.Session()
    
    # Headers to mimic browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://letterboxd.com/"
    }
    
    try:
        # First get the login page to get the CSRF token
        login_page = session.get("https://letterboxd.com/sign-in/", headers=headers)
        
        # Extract CSRF token from the page
        csrf_token = re.search(r'name="__csrf" value="([^"]+)"', login_page.text).group(1)
        
        # Login details with CSRF token
        login_data = {
            "username": os.getenv("LETTERBOXD_USERNAME"),
            "password": os.getenv("LETTERBOXD_PASSWORD"),
            "__csrf": csrf_token
        }
        
        # Login
        session.post("https://letterboxd.com/sign-in/", data=login_data, headers=headers)
        
        # Get the movie page first to get a new CSRF token
        movie_page = session.get("https://letterboxd.com/film/good/", headers=headers)
        new_csrf_token = re.search(r'data-csrf="([^"]+)"', movie_page.text).group(1)
        
        # Add to watchlist with CSRF token in headers
        watchlist_url = "https://letterboxd.com/film/good/add-to-watchlist/"
        headers["X-CSRF-Token"] = new_csrf_token
        
        response = session.post(watchlist_url, headers=headers)
        
        if response.status_code == 200:
            print("Successfully added to watchlist!")
            print(response.text)
        else:
            print(f"Failed to add to watchlist. Status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_to_letterboxd_watchlist()