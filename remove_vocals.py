import os
import torchaudio
from openunmix import predict
import librosa
import numpy as np

def remove_silence_and_pad(audio, sample_rate, padding_duration=2):
    # Remove silence from the beginning and end
    audio_np = audio.numpy()
    
    # Find the indices of non-silent parts
    non_silent_indices = librosa.effects.split(audio_np, top_db=20)
    
    # If there are no non-silent parts, return the original audio with padding
    if len(non_silent_indices) == 0:
        padding = np.zeros(int(sample_rate * padding_duration))
        return np.concatenate((padding, audio_np, padding))
    
    # Get the start and end of the non-silent segments
    start = non_silent_indices[0][0]
    end = non_silent_indices[-1][1]
    
    # Trim the audio to remove silence at the beginning and end
    audio_trimmed = audio_np[start:end]
    
    # Add padding
    padding = np.zeros(int(sample_rate * padding_duration))
    audio_padded = np.concatenate((padding, audio_trimmed, padding))
    
    return audio_padded

def remove_vocals(input_dirs, output_dirs):
    for input_dir, output_dir in zip(input_dirs, output_dirs):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        model = predict.load_model()

        # Process each audio file in the input directory
        for filename in os.listdir(input_dir):
            if filename.endswith('.mp3') or filename.endswith('.wav'):
                input_file = os.path.join(input_dir, filename)
                print(f"Removing vocals from: {input_file}")

                # Load the audio
                audio, sample_rate = torchaudio.load(input_file)

                # Remove silence and add padding
                audio_processed = remove_silence_and_pad(audio, sample_rate)

                # Remove vocals
                instrumental = predict.separate(model, audio_processed)

                # Save the result
                output_file = os.path.join(output_dir, filename)
                torchaudio.save(output_file, instrumental, sample_rate)

                print(f"Vocal removed and saved in: {output_file}")

if __name__ == "__main__":
    BASE_DIR = os.getenv('BASE_DIR')
    
    BASE_INPUT_DIR = os.path.join(BASE_DIR, 'audio')
    INPUT_ORIGINAL_DIR = os.path.join(BASE_INPUT_DIR, 'original')
    INPUT_PIANO_DIR = os.path.join(BASE_INPUT_DIR, 'piano')
    
    BASE_OUTPUT_DIR = os.path.join(BASE_DIR, 'instrumental_only')
    OUTPUT_ORIGINAL_DIR = os.path.join(BASE_OUTPUT_DIR, 'original')
    OUTPUT_PIANO_DIR = os.path.join(BASE_OUTPUT_DIR, 'piano')

    remove_vocals([INPUT_ORIGINAL_DIR, INPUT_PIANO_DIR], [OUTPUT_ORIGINAL_DIR, OUTPUT_PIANO_DIR]) 