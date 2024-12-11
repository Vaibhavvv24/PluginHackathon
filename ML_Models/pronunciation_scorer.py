import os
import subprocess
from speech_recognition import Recognizer, AudioFile
import pyttsx3  # Open-source TTS library
import difflib
import pocketsphinx  # Open-source phoneme extractor

# Directory for intermediate files
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Transcribe the original audio to text using STT (Speech-to-Text)
def transcribe_audio(audio_path, recognizer, language='en-US'):
    with AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio, language=language)  # Google STT is free with limits
    return text

# 2. Convert text back to speech using pyttsx3 (Text-to-Speech)
def synthesize_audio(text, output_path):
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()

# 3. Extract phonemes using PocketSphinx
def extract_phonemes_pocketsphinx(audio_path):
    try:
        # Initialize PocketSphinx configuration
        config = pocketsphinx.Decoder.default_config()
        config.set_string('-hmm', pocketsphinx.get_model_path() + '/en-us')  # Acoustic model
        config.set_string('-lm', pocketsphinx.get_model_path() + '/en-us.lm.bin')  # Language model
        config.set_string('-dict', pocketsphinx.get_model_path() + '/cmudict-en-us.dict')  # Phonetic dictionary
        
        # Run the decoder on the audio file
        decoder = pocketsphinx.Decoder(config)
        decoder.start_utt()
        
        with open(audio_path, 'rb') as audio_file:
            decoder.process_raw(audio_file.read(), full_utt=True)
        decoder.end_utt()
        
        # Extract phonemes from the alignment
        phonemes = []
        for seg in decoder.seg():
            phonemes.append(seg.word)  # Append recognized phoneme/word
        
        return ' '.join(phonemes)
    except Exception as e:
        print(f"Error during PocketSphinx phoneme extraction: {e}")
        return None

# 4. Compare phoneme sequences (to focus on pronunciation only)
def compare_phonemes(phonemes1, phonemes2):
    # Sequence matching to compute phoneme similarity using difflib
    seq_matcher = difflib.SequenceMatcher(None, phonemes1, phonemes2)
    similarity = seq_matcher.ratio()
    return similarity

# 5. Main function to orchestrate the steps
def analyze_pronunciation(original_audio, synthesized_audio, transcription):
    # Extract phonemes using PocketSphinx for original and synthesized audio
    print("Extracting phonemes from original audio...")
    original_phonemes = extract_phonemes_pocketsphinx(original_audio)
    
    print("Extracting phonemes from synthesized audio...")
    synthesized_phonemes = extract_phonemes_pocketsphinx(synthesized_audio)

    if original_phonemes is None or synthesized_phonemes is None:
        print("Error: Could not extract phonemes.")
        return None
    
    # Compare phoneme sequences to evaluate pronunciation similarity
    similarity = compare_phonemes(original_phonemes, synthesized_phonemes)
    return similarity

if __name__ == "__main__":
    # Paths to audio files
    original_audio_path = "original_audio.wav"
    synthesized_audio_path = os.path.join(OUTPUT_DIR, "synthesized_audio.wav")
    
    # Recognizer for transcription
    recognizer = Recognizer()

    # Step 1: Transcribe original audio to text
    print("Transcribing original audio...")
    transcription = transcribe_audio(original_audio_path, recognizer)
    print(f"Transcription: {transcription}")

    # Step 2: Generate synthesized audio from transcription
    print("Synthesizing audio from transcription...")
    synthesize_audio(transcription, synthesized_audio_path)

    # Step 3-4: Compare phoneme sequences and evaluate pronunciation
    print("Analyzing pronunciation...")
    similarity_score = analyze_pronunciation(original_audio_path, synthesized_audio_path, transcription)

    if similarity_score is not None:
        print(f"Pronunciation Similarity Score: {similarity_score:.2f}")
    else:
        print("Failed to compute similarity.")