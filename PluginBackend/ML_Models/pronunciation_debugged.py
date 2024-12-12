import os
import librosa
import numpy as np
import librosa.display
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import soundfile as sf

def convert_to_wav(input_path, output_path):
    """Convert audio files to .wav format if needed."""
    try:
        if not input_path.endswith('.wav'):
            import pydub
            audio = pydub.AudioSegment.from_file(input_path)
            audio.export(output_path, format='wav')
        else:
            # Copy as the target wav
            os.rename(input_path, output_path)
    except ImportError:
        raise Exception("Please install pydub and ffmpeg for audio conversion")

def calculate_pronunciation_score(original_audio_path, ideal_audio_path):
    # Load both audio files
    original_audio, original_sr = librosa.load(original_audio_path, sr=16000)  # Resampling to 16kHz
    ideal_audio, ideal_sr = librosa.load(ideal_audio_path, sr=16000)
    
    # Ensure audio is resampled to the same rate
    assert original_sr == ideal_sr, "Sampling rates of both audio files must match"
    
    # Extract MFCC features
    original_mfcc = librosa.feature.mfcc(y=original_audio, sr=original_sr, n_mfcc=13)
    ideal_mfcc = librosa.feature.mfcc(y=ideal_audio, sr=ideal_sr, n_mfcc=13)
    
    # Compute DTW distance between MFCC features
    distance, _ = fastdtw(original_mfcc.T, ideal_mfcc.T, dist=euclidean)
    
    # Normalize distance to a score (the lower the distance, the higher the score)
    max_distance = max(len(original_audio), len(ideal_audio))
    pronunciation_score = max(0, 100 - (distance / max_distance) * 100)  # Scale to 0-100
    
    return pronunciation_score
#convert_to_wav(r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\live-recording_PO3qhU1.mp3",r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\ref_wav\new.wav")
print(calculate_pronunciation_score(r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\ref_wav\vai.wav",r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\wavfiles\aunt.wav"))