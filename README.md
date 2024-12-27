# YouTube Playlist to Letterboxd watchlist 

The core idea is, since YouTube is my source for trailers or movie reviews and stuff, whenever I add a film related video to a specific playlist, it should automatically be added to my Letterboxd watchlist.

YouTube has an API, Letterboxd doesn't.

### `YouTube PLaylist to Letterboxd watchlist Updation`
Add a film trailer to a specific playlist on YouTube:

![image](https://github.com/user-attachments/assets/27c523d4-0a5e-4fd8-afad-949ee38c3bf8)


Find it on your Letterboxd watchlist:

![image](https://github.com/user-attachments/assets/60fc92b9-4c00-4e7f-9feb-4591b3612f5e)


Steps to work with it:
1. create a `.env` file in the same directory and add the following credentials: YouTube Playlist ID, Letterboxd Password, and Letterboxd Username.
2. run `Letterboxd-YT.py`
3. you can also run a script using cronjob to automatically run this every day or so
