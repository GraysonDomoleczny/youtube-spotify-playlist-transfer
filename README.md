# YouTube to Spotify Playlist Transfer Tool

A Python desktop application that transfers songs from YouTube playlists to Spotify playlists. The application uses the YouTube playlist URL to retrieve song information, searches Spotify for matching tracks, and adds the results to an existing or newly created Spotify playlist.

## Features

* Transfer songs from YouTube playlists to Spotify
* Create a new Spotify playlist or add songs to an existing playlist
* Spotify OAuth authentication
* Tkinter graphical user interface
* YouTube playlist metadata extraction using `yt-dlp`
* Spotify track searching and matching
* Transfer progress tracking
* Input validation and error handling
* Playlist name, description, and visibility options when creating a new playlist

## Technologies

* **Python**
* **Tkinter** – GUI
* **Spotipy** – Spotify Web API integration
* **yt-dlp** – YouTube playlist metadata extraction
* **Spotify Web API** – Authentication, playlist management, and track searching

## How It Works

1. Enter your Spotify API credentials.
2. Authenticate with your Spotify account.
3. Enter a YouTube playlist URL.
4. Choose an existing Spotify playlist or create a new one.
5. The application extracts the songs from the YouTube playlist.
6. Each song is searched for on Spotify.
7. Matching tracks are added to the selected Spotify playlist.
8. The GUI displays the transfer progress and any errors encountered.

## Setup

### 1. Install Python

Make sure Python is installed on your system.

### 2. Install Dependencies

```bash
pip install yt-dlp spotipy
```

Tkinter is included with most standard Python installations.

### 3. Create a Spotify Application

Create an application through the Spotify Developer Dashboard and obtain:

* Client ID
* Client Secret
* Redirect URI

The Redirect URI configured in the application must match the one used by the program.

### 4. Run the Application

```bash
python main.py
```

Enter the required Spotify credentials and YouTube playlist information through the application.

## Notes

The application relies on Spotify's search results to find matching tracks. Because YouTube and Spotify may use different song titles, artist names, or formatting, some tracks may not be matched correctly.

Spotify API access and authentication requirements may change over time. Check Spotify's developer documentation if authentication or API access no longer works as expected.

## Project Purpose

This project was created to practice Python application development, graphical user interfaces, API integration, OAuth authentication, data processing, and working with third-party libraries.
