import os
from spleeter.separator import Separator

def remove_vocals(input_dirs: list[str], output_dirs: list[str]) -> None:
    separator = Separator('spleeter:2stems')

    for input_dir, output_dir in zip(input_dirs, output_dirs):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Process each audio file in the input directory
        for filename in os.listdir(input_dir):
            if filename.endswith('.mp3') or filename.endswith('.wav'):
                input_file = os.path.join(input_dir, filename)
                print(f"Removing vocals from: {input_file}")

                separator.separate_to_file(input_file, output_dir)
                print(f"Instrumental saved to: {output_dir}")

if __name__ == "__main__":
    BASE_DIR = os.getenv('BASE_DIR')
    
    BASE_INPUT_DIR = os.path.join(BASE_DIR, 'audio')
    INPUT_ORIGINAL_DIR = os.path.join(BASE_INPUT_DIR, 'original')
    INPUT_PIANO_DIR = os.path.join(BASE_INPUT_DIR, 'piano')
    
    BASE_OUTPUT_DIR = os.path.join(BASE_DIR, 'instrumental_only')
    OUTPUT_ORIGINAL_DIR = os.path.join(BASE_OUTPUT_DIR, 'original')
    OUTPUT_PIANO_DIR = os.path.join(BASE_OUTPUT_DIR, 'piano')

    remove_vocals([INPUT_ORIGINAL_DIR, INPUT_PIANO_DIR], [OUTPUT_ORIGINAL_DIR, OUTPUT_PIANO_DIR]) 