import spotipy
import pandas as pd
import os
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')))

# Function to search for video on YouTube
def search_video(track_name, video_type='piano', cache={}):
    if track_name in cache:
        print(f"Cache hit for track: {track_name}")
        return cache[track_name]
    
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
            if (video_type == 'original' and ('original' in title or 'oficial' in title)) or \
               (video_type == 'piano' and ('piano solo' in title or 'piano cover' in title or 'piano' in title)):
                video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                
                cache[track_name] = video_url
                return video_url
        
        cache[track_name] = None
        return None
    except Exception as e:
        print(f"Error searching for video for {track_name}: {e}")
        return None

# Function to fetch metadata from a playlist
def fetch_playlist_metadata(playlist_url):
    playlist_id = playlist_url.split('/')[-1].split('?')[0] 
    
    if not playlist_id:
        print("Error: Playlist ID not found.")
        return None 

    spotify_playlist_id_length = 22
    # Verify if the playlist ID is valid
    if len(playlist_id) != spotify_playlist_id_length:
        print("Error: Invalid playlist ID.")
        return None

    playlist = sp.playlist_tracks(playlist_id)
    
    music_data = []

    for item in playlist['items']:
        track = item['track']
        track_name = track.get('name', None)
        artist_name = track['artists'][0].get('name', None) if track['artists'] else None
        album_name = track['album'].get('name', None) if track.get('album') else None
        release_date = track['album'].get('release_date', None) if track.get('album') else None
        duration_ms = track.get('duration_ms', None)
        track_url = track['external_urls'].get('spotify', None) if track.get('external_urls') else None

        # Search for YouTube piano solo video
        video_piano_solo_url = search_video(track_name, video_type='piano')

        # Search for YouTube original video
        video_original_url = search_video(track_name, video_type='original')

        # Append track data to the list
        music_data.append({
            'Track Name': track_name,
            'Artist': artist_name,
            'Album': album_name,
            'Release Date': release_date,
            'Duration (ms)': duration_ms,
            'Spotify Track URL': track_url,
            'YouTube Piano Solo Video URL': video_piano_solo_url,
            'YouTube Original Video URL': video_original_url
        })
        
        print(f"Processed track: {track_name} by {artist_name}")
    
    # Create a DataFrame with the track metadata
    df = pd.DataFrame(music_data)

    # Convert duration from milliseconds to minutes:seconds
    df['Duration (min:sec)'] = df['Duration (ms)'].apply(lambda x: f"{x // 60000}:{(x % 60000) // 1000:02d}" if x is not None else None)

    # Save the DataFrame to a CSV file
    df.to_csv(os.path.join(os.getenv('BASE_DIR'), 'playlist_metadata.csv'), index=False)

    print(df)

    return df

if __name__ == "__main__":
    playlist_url = f'https://open.spotify.com/playlist/{os.getenv("SPOTIFY_PLAYLIST_ID")}'
    df_metadata = fetch_playlist_metadata(playlist_url)