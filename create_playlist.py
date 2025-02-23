import os
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd  # Importando pandas para manipulação de dados

load_dotenv()

# Function to authenticate with Spotify
def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'), 
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri='http://localhost:8888/callback', 
        scope=["playlist-modify-public", "playlist-modify-private"]
    ))
    return sp

# Function to search for a song on Spotify
def search_song_spotify(sp, title, artist):
    query = f"track:{title} artist:{artist}"
    result = sp.search(query, type='track', limit=1)
    
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        return track['id']
    else:
        return None

# Function to save the missing tracks in a CSV file
def save_missing_tracks(not_found_songs):
    df_missing = pd.DataFrame(not_found_songs, columns=['Title', 'Artist'])
    missing_tracks_file = os.path.join(os.getenv('BASE_DIR'), 'missing_tracks.csv')
    df_missing.to_csv(missing_tracks_file, index=False)
    print(f"Missing tracks saved to {missing_tracks_file}")

# Function to create a playlist on Spotify and add songs to it
def create_playlist_with_songs(sp, songs):
    user_id = sp.current_user()['id']
    
    # Create a new playlist
    playlist = sp.user_playlist_create(user_id, name="MPB Playlist", public=True, description="Playlist de músicas populares do MPB")
    playlist_id = playlist['id']
    
    # Add songs to the playlist
    track_ids = []
    not_found_songs = [] 
    for title, artist in songs:
        track_id = search_song_spotify(sp, title, artist)
        if track_id:
            track_ids.append(track_id)
            print(f"Track found and added: {title} by {artist}")
        else:
            not_found_songs.append((title, artist)) 
            print(f"Track not found: {title} by {artist}")
    
    # Add songs to the playlist in groups of 100
    while track_ids:
        sp.playlist_add_items(playlist_id, track_ids[:100])
        track_ids = track_ids[100:]
        print(f"Added 100 tracks to the playlist. Remaining tracks: {len(track_ids)}")

    if not track_ids:
        print("Playlist created successfully.")

    # Inform the tracks that were not added
    if not_found_songs:
        print(f"Total missing tracks: {len(not_found_songs)}")
        save_missing_tracks(not_found_songs)

# Function to scrape the MPB songs from letras.mus.br
def get_mpb_songs():
    url = "https://www.letras.mus.br/mais-acessadas/mpb/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    songs = []
    for item in soup.select('ol.top-list_mus li a'):
        title = item.get('title')
        artist = item.find('span', {'class': 'font --base --size14'}).text.strip() if item.find('span', {'class': 'font --base --size14'}) else 'Unknown Artist'
        songs.append((title, artist))
    
    return songs 

if __name__ == "__main__":
    # Step 1: Get the MPB songs from letras.mus.br
    print("Getting popular MPB songs...")
    songs = get_mpb_songs()
    print(f"Found {len(songs)} songs.")
    
    # Step 2: Authenticate with Spotify
    sp = authenticate_spotify()
    
    # Step 3: Create the playlist on Spotify and add the songs
    create_playlist_with_songs(sp, songs)