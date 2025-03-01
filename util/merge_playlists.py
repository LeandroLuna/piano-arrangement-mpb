import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import time
import requests

# Load environment variables
load_dotenv()

# Function to authenticate with Spotify
def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'), 
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri='http://localhost:8888/callback', 
        scope=["playlist-modify-public", "playlist-modify-private"],
        requests_timeout=15
    ))
    return sp

# Function to create a new playlist
def create_playlist(sp, name, description):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name=name, public=True, description=description)
    return playlist['id']

# Function to extract track ids from a playlist
def extract_track_ids(items, added_tracks):
    track_ids = []
    for item in items:
        track = item['track']
        if track:
            track_id = track['id']
            if track_id not in added_tracks:
                added_tracks.append(track_id)
                track_ids.append(track_id)
                print(f"Adding track: {track['name']} by {track['artists'][0]['name']}")
    return track_ids

# Function to fetch tracks from a playlist
def fetch_playlist_tracks(sp, playlist_id, offset, retries):
    for attempt in range(retries):
        try:
            return sp.playlist_tracks(playlist_id, offset=offset)
        except requests.exceptions.ReadTimeout:
            print(f"Timeout occurred, retrying... ({attempt + 1}/{retries})")
            time.sleep(2)
    print("Failed to fetch tracks after multiple attempts.")
    return None

# Function to get tracks from a playlist
def get_tracks_from_playlist(sp, playlist_id, retries=10):
    added_tracks = []
    offset = 0

    while True:
        results = fetch_playlist_tracks(sp, playlist_id, offset, retries)
        if results is None or not results['items']:
            break
        
        added_tracks.extend(extract_track_ids(results['items'], added_tracks))
        offset += len(results['items'])
    
    return added_tracks

# Function to add tracks to a playlist
def add_tracks_to_playlist(sp, playlist_id, track_ids):
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i + 100])

# Function to merge playlists
def merge_playlists(sp, playlist_ids, new_playlist_name, new_playlist_description):
    new_playlist_id = create_playlist(sp, new_playlist_name, new_playlist_description)
    added_tracks = []

    for playlist_id in playlist_ids:
        print(f"\nMerging playlist number {playlist_ids.index(playlist_id) + 1} of {len(playlist_ids)}: {playlist_id}")
        added_tracks.extend(get_tracks_from_playlist(sp, playlist_id))

    # Add tracks to the new playlist in batches of 100
    add_tracks_to_playlist(sp, new_playlist_id, added_tracks)

    print(f"Successfully created the playlist '{new_playlist_name}' with {len(added_tracks)} tracks.")


if __name__ == "__main__":
    sp = authenticate_spotify()
    
    playlist_ids = [
        '6sWNtqsq1ip2quKm6U3UvD',
        '2dFYbLO2e91eiXispfv616',
        '2OZVlENh6kAfqpRyPIPyl7',
        '4ayAVkzotycmtUPKCHimZX',
        '11K7xZTHsbSJHiYVY0Nkp9'
    ]
    
    unified_playlist_name = "Ultimate Piano Solo Covers Playlist"
    unified_playlist_description = "A unified playlist of piano solo cover songs."
    
    merge_playlists(sp, playlist_ids, unified_playlist_name, unified_playlist_description) 