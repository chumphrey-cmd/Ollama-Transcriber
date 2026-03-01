import torch
import os
import warnings
import numpy as np
import math
from pydub import AudioSegment
from src.audio.preprocess import preprocess_audio  # Import for audio preprocessing

# Suppress FutureWarning associated with torch.load (for compatibility)
warnings.filterwarnings("ignore", category=FutureWarning)

# Constants for chunk size, overlap, and target sample rate
CHUNK_SIZE = 30  # Seconds - Size of each audio chunk for transcription
OVERLAP = 4      # Seconds - Overlap between audio chunks for better context
TARGET_SAMPLE_RATE = 16000  # Hz - Target sample rate for audio processing and Whisper model

def transcribe_audio_chunk(audio_chunk, model, language="en"):
    """Transcribes a single audio chunk using the provided Whisper model.

    Args:
        audio_chunk (np.ndarray): The audio chunk as a NumPy array.
        model (whisper.model.Whisper): The loaded Whisper model.
        language (str): The language code to use (or None for auto-detect).

    Returns:
        str: The transcribed text.
        None: If there is an error during transcription.
    """
    try:
        audio_chunk = torch.tensor(audio_chunk, dtype=torch.float32).unsqueeze(0)  # Convert chunk to tensor for Whisper
        # MODIFIED: Replace hardcoded "en" with the dynamic language variable
        result = model.transcribe(audio_chunk.squeeze().numpy(), language=language, temperature=0.0)  # Transcribe the chunk
        return result['text']  # Return the transcribed text
    except Exception as e:
        print(f"Error transcribing audio chunk: {e}")
        return None

def process_audio_chunks(file_path, model, chunk_size=CHUNK_SIZE, overlap=OVERLAP, language="en"):
    """Processes an audio file in chunks and returns the combined transcription.

    Args:
        file_path (str): The path to the audio file.
        model (whisper.model.Whisper): The loaded Whisper model.
        chunk_size (int): The size of each chunk in seconds. Defaults to CHUNK_SIZE.
        overlap (int): The overlap between chunks in seconds. Defaults to OVERLAP.
        language (str): The language code to use (or None for auto-detect).

    Returns:
        str: The combined transcribed text.
        None: If there is an error during processing.
    """
    try:
        audio_segment = AudioSegment.from_file(file_path)  # Load audio file using pydub

        # Preprocess the audio (includes resampling, noise reduction, etc.)
        audio_segment = preprocess_audio(audio_segment) # Pass AudioSegment directly

        audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)  # Convert to NumPy array
        audio_np = audio_np / np.max(np.abs(audio_np))  # Normalize audio to [-1, 1] range

        num_chunks = math.ceil(len(audio_np) / (chunk_size * TARGET_SAMPLE_RATE))  # Calculate number of chunks
        print(f"Number of chunks: {num_chunks}")

        transcript = []  # Initialize an empty list to store transcribed chunks
        for i in range(num_chunks):
            # Calculate start and end indices for the current chunk with overlap
            start = int(i * chunk_size * TARGET_SAMPLE_RATE) - int(overlap * TARGET_SAMPLE_RATE)
            start = max(0, start)  # Ensure start index is not negative
            end = int((i + 1) * chunk_size * TARGET_SAMPLE_RATE)

            audio_chunk = audio_np[start:end]  # Extract the audio chunk

            if len(audio_chunk) == 0:  # Skip empty chunks
                continue

            print(f"Transcribing chunk {i+1}/{num_chunks}...")
            # MODIFIED: Pass the language variable down to the chunk transcriber
            chunk_transcript = transcribe_audio_chunk(audio_chunk, model, language)  # Transcribe the chunk

            if chunk_transcript:  # If transcription is successful
                print(f"Chunk {i+1} transcription: {chunk_transcript}")
                transcript.append(chunk_transcript)  # Add the transcription to the list

        return ' '.join(transcript)  # Join all transcribed chunks into a single string

    except Exception as e:
        print(f"Error processing audio chunks: {e}")
        return None


def transcribe_audio(input_file, output_dir, model, language="en"):
    """Transcribes a single audio file and saves the transcription to a text file.

    Args:
        input_file (str): Path to the input audio file.
        output_dir (str): Directory to save the transcription.
        model (whisper.model.Whisper): The loaded Whisper model.
        language (str): The language code to use (or None for auto-detect).
    """
    try:
        print(f"Transcribing {input_file}...")
        # MODIFIED: Pass the language variable into the chunk processor
        transcript = process_audio_chunks(input_file, model, language=language)  # Process audio chunks and transcribe

        if transcript:  # If transcription is successful
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.txt")  # Create output file path
            with open(output_file, 'w', encoding='utf-8') as f:  # Open file for writing
                f.write(transcript)  # Write the transcription to the file
            print(f"Transcription saved to: {output_file}")
        else:
            print("Transcription failed.")

    except Exception as e:
        print(f"Error in transcribe_audio: {e}")