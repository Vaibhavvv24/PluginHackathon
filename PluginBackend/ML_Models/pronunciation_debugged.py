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
    if a.shape != b.shape:
        min_len = min(a.shape[1], b.shape[1])
        a = a[:, :min_len]
        b = b[:, :min_len]
    return np.dot(a.flatten(), b.flatten()) / (np.linalg.norm(a.flatten()) * np.linalg.norm(b.flatten()))

# Manhattan Distance (L1 Norm) between two feature sets
def manhattan_distance(a, b):
    if a.shape != b.shape:
        min_len = min(a.shape[1], b.shape[1])
        a = a[:, :min_len]
        b = b[:, :min_len]
    return np.sum(np.abs(a - b))

# Mean Squared Error (MSE) between two feature sets
def mean_squared_error(a, b):
    if a.shape != b.shape:
        min_len = min(a.shape[1], b.shape[1])
        a = a[:, :min_len]
        b = b[:, :min_len]
    return np.mean((a - b) ** 2)

# Calculate Pitch Error
def calculate_pitch_error(original_audio, ideal_audio, sr):
    original_pitch = librosa.pyin(original_audio, fmin=librosa.note_to_hz('C1'), fmax=librosa.note_to_hz('C8'))
    ideal_pitch = librosa.pyin(ideal_audio, fmin=librosa.note_to_hz('C1'), fmax=librosa.note_to_hz('C8'))

    original_pitch = original_pitch[0] if original_pitch is not None else np.zeros_like(original_audio)
    ideal_pitch = ideal_pitch[0] if ideal_pitch is not None else np.zeros_like(ideal_audio)

    if len(original_pitch) != len(ideal_pitch):
        min_len = min(len(original_pitch), len(ideal_pitch))
        original_pitch = np.interp(np.linspace(0, len(original_pitch)-1, min_len), np.arange(len(original_pitch)), original_pitch)
        ideal_pitch = np.interp(np.linspace(0, len(ideal_pitch)-1, min_len), np.arange(len(ideal_pitch)), ideal_pitch)

    pitch_error = np.mean(np.abs(original_pitch - ideal_pitch))
    if np.isnan(pitch_error):
        return float('nan')
    return pitch_error

def calculate_pronunciation_score(original_audio_path, ideal_audio_path):
    original_audio, original_sr = librosa.load(original_audio_path, sr=16000)
    ideal_audio, ideal_sr = librosa.load(ideal_audio_path, sr=16000)
    
    assert original_sr == ideal_sr, "Sampling rates of both audio files must match"
    
    original_mfcc = librosa.feature.mfcc(y=original_audio, sr=original_sr, n_mfcc=13)
    ideal_mfcc = librosa.feature.mfcc(y=ideal_audio, sr=ideal_sr, n_mfcc=13)
    
    distance, _ = fastdtw(original_mfcc.T, ideal_mfcc.T, dist=euclidean)
    
    cosine_sim = cosine_similarity(original_mfcc, ideal_mfcc)
    manhattan_dist = manhattan_distance(original_mfcc, ideal_mfcc)
    mse = mean_squared_error(original_mfcc, ideal_mfcc)
    pitch_error = calculate_pitch_error(original_audio, ideal_audio, original_sr)
    
    max_distance = max(len(original_audio), len(ideal_audio))
    pronunciation_score = max(0, 100 - (distance / max_distance) * 100)
    
    # Convert results to float strings
    final_score = {
        "Pronunciation Score (DTW)": f"{float(pronunciation_score):.2f}",
        "Cosine Similarity": f"{float(cosine_sim):.4f}",
        "Manhattan Distance": f"{float(manhattan_dist):.2f}",
        "Mean Squared Error (MSE)": f"{float(mse):.2f}",
        "Pitch Error": f"{float(pitch_error):.2f}" if not np.isnan(pitch_error) else "NaN"
    }

    # Significance of values
    analysis = {
        "Pronunciation Score (DTW)": interpret_pronunciation_score(pronunciation_score),
        "Cosine Similarity": interpret_cosine_similarity(cosine_sim),
        "Manhattan Distance": interpret_manhattan_distance(manhattan_dist),
        "Mean Squared Error (MSE)": interpret_mse(mse),
        "Pitch Error": interpret_pitch_error(pitch_error)
    }

    print(final_score)
    print(analysis)
    return final_score, analysis

# Interpretation functions for each metric
def interpret_pronunciation_score(score):
    if score >= 90:
        return "Excellent pronunciation match."
    elif score >= 70:
        return "Good pronunciation match with slight differences."
    elif score >= 50:
        return "Moderate match, with noticeable differences."
    else:
        return "Poor pronunciation match, indicating significant differences."

def interpret_cosine_similarity(sim):
    if sim >= 0.9:
        return "Very high similarity between the features."
    elif sim >= 0.7:
        return "Good similarity."
    elif sim >= 0.4:
        return "Moderate similarity, with noticeable differences."
    else:
        return "Low similarity, indicating large differences."

def interpret_manhattan_distance(dist):
    if dist < 5000:
        return "Very similar features."
    elif dist < 20000:
        return "Moderate difference."
    elif dist < 50000:
        return "Noticeable difference in features."
    else:
        return "Significant feature differences, indicating very distinct audio characteristics."

def interpret_mse(mse):
    if mse < 500:
        return "Very small error, indicating very similar features."
    elif mse < 2000:
        return "Moderate error, with some differences in features."
    elif mse < 5000:
        return "Noticeable error, features differ significantly."
    else:
        return "High error, indicating large feature differences."

def interpret_pitch_error(pitch_error):
    if np.isnan(pitch_error):
        return "NaN (Could not calculate pitch)"
    elif pitch_error < 50:
        return "Excellent pitch match."
    elif pitch_error < 150:
        return "Moderate pitch match with noticeable differences."
    else:
        return "Significant pitch differences, poor match."


print(calculate_pronunciation_score(
    r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\audios\ref_wav\vai.wav",
    r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\media\wavfiles\aunt.wav"
))