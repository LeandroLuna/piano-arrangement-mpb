import os
import yt_dlp
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Function to download audio from a video using yt-dlp
def download_audio(video_url: str, output_path: str, index: int) -> None:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, f'{index:04d}.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

# Function to download audios from the metadata file
def download_audios_from_metadata(metadata_file: str, output_dir: str) -> None:
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the metadata file
    df = pd.read_csv(metadata_file)

    # Download audio for each found video
    for index, row in df.iterrows():
        # Use the original video URL and the piano cover video URL
        video_url_original = row.get('YouTube Original Video URL')
        video_url_piano = row.get('YouTube Piano Solo Video URL')
        
        if not video_url_original and not video_url_piano:
            print(f"No video URL found for {row['Track Name']} by {row['Artist']}")
            break

        if video_url_original:
            original_dir = os.path.join(output_dir, 'original')
            print(f"Downloading original audio: {video_url_original}")
            download_audio(video_url_original, original_dir, index)
            print(f"Original audio of '{row['Track Name']}' downloaded successfully!")

        if video_url_piano:
            piano_dir = os.path.join(output_dir, 'piano')
            print(f"Downloading piano cover audio: {video_url_piano}")
            download_audio(video_url_piano, piano_dir, index)
            print(f"Piano cover audio of '{row['Track Name']}' downloaded successfully!")

if __name__ == "__main__":
    METADATA_FILE = os.path.join(os.getenv('BASE_DIR'), 'playlist_metadata.csv')
    OUTPUT_DIR = os.path.join(os.getenv('BASE_DIR'), 'audio')

    download_audios_from_metadata(METADATA_FILE, OUTPUT_DIR) 