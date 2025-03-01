import os
from spleeter.separator import Separator

# Remove vocals from audio files
def remove_vocals(input_dirs: list[str], output_dirs: list[str]) -> None:
    # Initialize the separator with 2 stems (vocals and accompaniment)
    separator = Separator('spleeter:2stems')

    for input_dir, output_dir in zip(input_dirs, output_dirs):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Process each audio file in the input directory
        for filename in os.listdir(input_dir):
            if filename.endswith('.mp3'):
                input_file = os.path.join(input_dir, filename)
                print(f"Removing vocals from: {input_file}")

                # Create a temporary directory for the separated audio
                temp_output_path = os.path.join(output_dir, 'temp')
                
                # Separate the audio
                separator.separate_to_file(input_file, temp_output_path, filename_format='{instrument}.{codec}')
                
                # Move the accompaniment file to the final destination
                accompaniment_file = os.path.join(temp_output_path, filename.split('.')[0], 'accompaniment.wav')
                output_file = os.path.join(output_dir, filename)
                os.rename(accompaniment_file, output_file)
                
                # Clean up temporary files
                os.rmdir(os.path.join(temp_output_path, filename.split('.')[0]))
                os.rmdir(temp_output_path)
                
                print(f"Saved instrumental to: {output_file}")

if __name__ == "__main__":
    BASE_DIR = os.getenv('BASE_DIR')
    
    BASE_INPUT_DIR = os.path.join(BASE_DIR, 'audio')
    INPUT_ORIGINAL_DIR = os.path.join(BASE_INPUT_DIR, 'original')
    INPUT_PIANO_DIR = os.path.join(BASE_INPUT_DIR, 'piano')
    
    BASE_OUTPUT_DIR = os.path.join(BASE_DIR, 'instrumental_only')
    OUTPUT_ORIGINAL_DIR = os.path.join(BASE_OUTPUT_DIR, 'original')
    OUTPUT_PIANO_DIR = os.path.join(BASE_OUTPUT_DIR, 'piano')

    remove_vocals([INPUT_ORIGINAL_DIR, INPUT_PIANO_DIR], [OUTPUT_ORIGINAL_DIR, OUTPUT_PIANO_DIR]) 