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

# Cosine Similarity between two feature sets
def cosine_similarity(a, b):
    # Make sure both arrays have the same shape by padding or trimming them
    if a.shape != b.shape:
        min_len = min(a.shape[1], b.shape[1])
        a = a[:, :min_len]
        b = b[:, :min_len]
    return np.dot(a.flatten(), b.flatten()) / (np.linalg.norm(a.flatten()) * np.linalg.norm(b.flatten()))

# Manhattan Distance (L1 Norm) between two feature sets
def manhattan_distance(a, b):
    # Make sure both arrays have the same shape by padding or trimming them
    if a.shape != b.shape:
        min_len = min(a.shape[1], b.shape[1])
        a = a[:, :min_len]
        b = b[:, :min_len]
    return np.sum(np.abs(a - b))

# Mean Squared Error (MSE) between two feature sets
def mean_squared_error(a, b):
    # Make sure both arrays have the same shape by padding or trimming them
    if a.shape != b.shape:
        min_len = min(a.shape[1], b.shape[1])
        a = a[:, :min_len]
        b = b[:, :min_len]
    return np.mean((a - b) ** 2)

# Calculate Pitch Error
def calculate_pitch_error(original_audio, ideal_audio, sr):
    original_pitch, _ = librosa.pyin(original_audio, fmin=librosa.note_to_hz('C1'), fmax=librosa.note_to_hz('C8'))
    ideal_pitch, _ = librosa.pyin(ideal_audio, fmin=librosa.note_to_hz('C1'), fmax=librosa.note_to_hz('C8'))
    pitch_error = np.mean(np.abs(original_pitch - ideal_pitch))
    return pitch_error

def calculate_pronunciation_score(original_audio_path, ideal_audio_path):
    # Load both audio files
    original_audio, original_sr = librosa.load(original_audio_path, sr=16000)  # Resampling to 16kHz
    ideal_audio, ideal_sr = librosa.load(ideal_audio_path, sr=16000)
    
    # Ensure audio is resampled to the same rate
    assert original_sr == ideal_sr, "Sampling rates of both audio files must match"
    
    # Extract MFCC features
    original_mfcc = librosa.feature.mfcc(y=original_audio, sr=original_sr, n_mfcc=13)
    ideal_mfcc = librosa.feature.mfcc(y=ideal_audio, sr=ideal_sr, n_mfcc=13)
    
    # Compute DTW distance between MFCC features (Euclidean)
    distance, _ = fastdtw(original_mfcc.T, ideal_mfcc.T, dist=euclidean)
    
    # Cosine Similarity
    cosine_sim = cosine_similarity(original_mfcc, ideal_mfcc)
    
    # Manhattan Distance
    manhattan_dist = manhattan_distance(original_mfcc, ideal_mfcc)
    
    # MSE (Mean Squared Error)
    mse = mean_squared_error(original_mfcc, ideal_mfcc)
    
    # Pitch Error
    pitch_error = calculate_pitch_error(original_audio, ideal_audio, original_sr)
    
    # Normalize DTW distance to a score (the lower the distance, the higher the score)
    max_distance = max(len(original_audio), len(ideal_audio))
    pronunciation_score = max(0, 100 - (distance / max_distance) * 100)  # Scale to 0-100
    
    # Combine all metrics into a final score (you can use any combination or weighting)
    final_score = {
        "Pronunciation Score (DTW)": pronunciation_score,
        "Cosine Similarity": cosine_sim,
        "Manhattan Distance": manhattan_dist,
        "Mean Squared Error (MSE)": mse,
        "Pitch Error": pitch_error
    }
    
    return final_score

# Example usage
# convert_to_wav(r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\live-recording_PO3qhU1.mp3",r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\ref_wav\new.wav")
print(calculate_pronunciation_score(
    r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\ref_wav\vai.wav",
    r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\wavfiles\aunt.wav"
))