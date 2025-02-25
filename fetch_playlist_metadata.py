import spotipy
import pandas as pd
import os
import isodate
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')))

def convert_duration_to_ms(duration):
    duration_obj = isodate.parse_duration(duration)
    return int(duration_obj.total_seconds() * 1000)

# Function to search for video on YouTube
def search_video(track_name, video_type):
    # Build the query based on the video type
    query = f"{track_name} original/oficial" if video_type == 'original' else f"{track_name} piano solo/cover"
    
    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            videoDefinition="high",
            maxResults=5
        )
        response = request.execute()

        # Checks if the video's title contains the word "piano" or "original"
        for item in response['items']:
            title = item['snippet']['title'].lower()
            if (video_type == 'original') or \
               (video_type == 'piano' and 'piano' in title):
                video_id = item['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                # Get youtube video duration
                video_details = youtube.videos().list(part='contentDetails', id=video_id).execute()
                duration = video_details['items'][0]['contentDetails']['duration'] if video_details['items'] else None
                duration_ms = convert_duration_to_ms(duration) if duration else None
                return video_url, duration_ms
        
        return None, None
    except Exception as e:
        if "403" in str(e):  # Check if the error is a 403, quota exceeded.
            print(f"Error 403 encountered for {track_name}: {e}")
            return "ERROR_403", None  # Return a specific value to indicate the error
        else:
            print(f"Error searching for video for {track_name}: {e}")
            return None, None

def load_existing_metadata(metadata_file_path):
    if os.path.exists(metadata_file_path):
        df_existing = pd.read_csv(metadata_file_path)
        return len(df_existing), df_existing
    return 0, pd.DataFrame()

def extract_track_data(track):
    track_name = track.get('name', None)
    artist_name = track['artists'][0].get('name', None) if track['artists'] else None
    album_name = track['album'].get('name', None) if track.get('album') else None
    release_date = track['album'].get('release_date', None) if track.get('album') else None
    duration_ms = track.get('duration_ms', None)
    track_url = track['external_urls'].get('spotify', None) if track.get('external_urls') else None

    if track_name is None:
        return None

    return {
        'Track Name': track_name,
        'Artist': artist_name,
        'Album': album_name,
        'Release Date': release_date,
        'Spotify Duration (ms)': duration_ms,
        'Spotify Track URL': track_url
    }

def save_metadata(music_data, df_existing, metadata_file_path):
    df_new = pd.DataFrame(music_data)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_csv(metadata_file_path, index=False)

# Function to fetch metadata from a playlist
def fetch_playlist_metadata():
    playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')
    if not playlist_id:
        return None

    metadata_file_path = os.path.join(os.getenv('BASE_DIR'), 'playlist_metadata.csv')
    last_index, df_existing = load_existing_metadata(metadata_file_path)

    playlist = sp.playlist_tracks(playlist_id)
    music_data = []

    for index, item in enumerate(playlist['items']):
        if index < last_index:
            continue
        
        track_data = extract_track_data(item['track'])
        if track_data is None:
            break

        video_piano_solo_url, video_piano_duration = search_video(track_data['Track Name'], video_type='piano')
        if video_piano_solo_url == "ERROR_403":
            break

        video_original_url, video_original_duration = search_video(track_data['Track Name'], video_type='original')
        if video_original_url == "ERROR_403":
            break

        music_data.append({
            **track_data,
            'YouTube Original Video URL': video_original_url,
            'Original Duration': video_original_duration,
            'YouTube Piano Solo Video URL': video_piano_solo_url,
            'Piano Solo Duration': video_piano_duration,
        })
        
        print(f"Processed track: {track_data['Track Name']} by {track_data['Artist']}")

    save_metadata(music_data, df_existing, metadata_file_path)

if __name__ == "__main__":
    fetch_playlist_metadata()