from pydub import AudioSegment
from pydub.silence import split_on_silence
import wave
import os
import json
import nltk
from nltk.tokenize import word_tokenize
from vosk import Model, KaldiRecognizer

# Download NLTK data (only run this once)

# nltk.download('punkt')
# nltk.download('punkt_tab')

# Define filler words
filler_words = {"uh", "um", "like", "you know", "actually", "basically"}

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file, wav_file):
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")
    print(f"Converted {mp3_file} to {wav_file}")

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
    return word_count / 1  # Assuming an average speaking rate of 1 minute for simplicity

# Function to analyze pause patterns based on silence durations
def analyze_pauses(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    
    # Split the audio by silence
    chunks = split_on_silence(audio, min_silence_len=1000, silence_thresh=-40)  # Adjust silence threshold as needed
    
    pauses = []
    current_position = 0  # Track the current position in the audio
    
    for chunk in chunks:
        chunk_duration = len(chunk)  # Length of the chunk in milliseconds
        next_position = current_position + chunk_duration
        
        # Calculate the silence (pause) duration between chunks
        pause_duration = (next_position - current_position) / 1000.0  # Convert to seconds
        if pause_duration > 1:  # Consider pauses longer than 1 second
            pauses.append(pause_duration)
        
        # Update the current position
        current_position = next_position
    
    return pauses

# Function to analyze filler word usage
def analyze_filler_words(text):
    words = word_tokenize(text.lower())
    filler_word_count = sum(1 for word in words if word in filler_words)
    return filler_word_count

# Function to calculate fluency score
def calculate_fluency_score(speaking_rate, pause_count, filler_word_count):
    fluency_score = 100
    fluency_score -= filler_word_count * 2  # Penalize for filler words
    fluency_score -= pause_count * 3  # Penalize for pauses
    fluency_score -= abs(speaking_rate - 120) * 0.5  # Adjust for speaking rate (120 words/min)
    fluency_score = max(0, fluency_score)  # Ensure non-negative score
    return fluency_score

# Main function to analyze the audio
def analyze_audio(audio_file, model_path='model'):
    print("Converting MP3 to WAV... (if applicable)")
    
    # Check if the file is MP3, if so, convert to WAV
    wav_file = audio_file.replace(".mp3", ".wav")
    if audio_file.endswith(".mp3"):
        convert_mp3_to_wav(audio_file, wav_file)
        audio_file = wav_file
    
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
audio_file = 'live-recording_Tx5NXRQ.mp3'  # Path to your audio file
model_path = 'vosk-model-en-in-0.5'  # Path to your Vosk model
analyze_audio(audio_file, model_path)
