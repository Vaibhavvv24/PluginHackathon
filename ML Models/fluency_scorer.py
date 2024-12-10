import wave
import math
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import json
import nltk
from nltk.tokenize import word_tokenize
from vosk import Model, KaldiRecognizer

# Download NLTK data (only run this once)
nltk.download('punkt')

# Define filler words
filler_words = {"uh", "um", "like", "you know", "actually", "basically"}

# Function to transcribe audio to text using Vosk
def transcribe_audio(audio_file, model_path='model'):
    # Initialize the Vosk model
    if not os.path.exists(model_path):
        raise ValueError(f"Model not found at path: {model_path}")
    model = Model(model_path)
    
    wf = wave.open(audio_file, "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())

    result_text = ''
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result_text += json.loads(recognizer.Result())['text'] + ' '
    
    # Finalize result
    result_text += json.loads(recognizer.FinalResult())['text']
    return result_text

# Function to calculate speaking rate (words per minute)
def calculate_speaking_rate(text):
    words = word_tokenize(text)
    word_count = len([word for word in words if word.isalpha()])
    # Assuming average speaking time of 1 minute for simplicity (real value could be estimated based on audio length)
    return word_count / 1  # This can be adjusted with a real time duration of the audio

# Function to calculate pause patterns based on silence durations
def analyze_pauses(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    # Split the audio by silence
    chunks = split_on_silence(audio, min_silence_len=1000, silence_thresh=-40)  # Adjust silence threshold as needed
    pauses = []
    for i in range(1, len(chunks)):
        pause_duration = (chunks[i].start_time - chunks[i-1].end_time) / 1000  # in seconds
        if pause_duration > 1:  # Pauses longer than 1 second
            pauses.append(pause_duration)
    return pauses

# Function to analyze filler word usage
def analyze_filler_words(text):
    words = word_tokenize(text.lower())
    filler_word_count = sum(1 for word in words if word in filler_words)
    return filler_word_count

# Function to calculate fluency score
def calculate_fluency_score(speaking_rate, pause_count, filler_word_count):
    fluency_score = 100
    # Penalize for filler words and pauses
    fluency_score -= filler_word_count * 2  # Each filler word reduces the fluency score
    fluency_score -= pause_count * 3  # Longer pauses reduce the fluency score
    fluency_score -= abs(speaking_rate - 120) * 0.5  # Adjust based on ideal speaking rate (e.g., 120 words per minute)
    fluency_score = max(0, fluency_score)  # Ensure the score is not negative
    return fluency_score

# Main function to analyze the audio
def analyze_audio(audio_file, model_path='model'):
    print("Transcribing audio...")
    text = transcribe_audio(audio_file, model_path)
    if not text:
        print("Failed to transcribe audio")
        return

    print("Analyzing speaking rate...")
    speaking_rate = calculate_speaking_rate(text)
    print(f"Speaking Rate: {speaking_rate} words per minute")

    print("Analyzing pauses...")
    pauses = analyze_pauses(audio_file)
    pause_count = len(pauses)
    print(f"Number of pauses greater than 1 second: {pause_count}")
    
    print("Analyzing filler words...")
    filler_word_count = analyze_filler_words(text)
    print(f"Filler words count: {filler_word_count}")

    print("Calculating fluency score...")
    fluency_score = calculate_fluency_score(speaking_rate, pause_count, filler_word_count)
    print(f"Fluency Score: {fluency_score:.2f}")

# Example usage
audio_file = 'your_audio_file.wav'  # Path to your audio file
model_path = 'path_to_vosk_model'  # Path to your Vosk model
analyze_audio(audio_file, model_path)