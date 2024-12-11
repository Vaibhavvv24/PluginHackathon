import os
import torch
import whisper
import librosa

# Load the Whisper model (medium model in this case)
model_m = whisper.load_model("medium")

def process_audio(file_path):
    # # Create output directories for transcriptions and translations
    # transcription_dir = os.path.join(output_dir, "transcriptions")
    # translation_dir = os.path.join(output_dir, "translations")
    # os.makedirs(transcription_dir, exist_ok=True)
    # os.makedirs(translation_dir, exist_ok=True)
    
    # Load and resample audio to 16kHz
    audio, sr = librosa.load(file_path, sr=16000)
    chunk_duration = 60  # Process audio in 60-second chunks
    transcription_result = []  # Store each chunk's transcription

    # Detect language once on a sample of the audio
    sample_audio = whisper.pad_or_trim(torch.tensor(audio[:sr * chunk_duration]))
    mel = whisper.log_mel_spectrogram(sample_audio).to(model_m.device)
    _, probs = model_m.detect_language(mel)
    detected_language = max(probs, key=probs.get)
    print(f"Detected language: {detected_language}")

    # Set decoding options for faster processing
    options = whisper.DecodingOptions(beam_size=2, temperature=0.7, fp16=False)

    for i in range(0, len(audio), chunk_duration * sr):
        # Process the larger chunk
        chunk = audio[i:i + chunk_duration * sr]
        whisper_audio = whisper.pad_or_trim(torch.tensor(chunk))

        # Generate mel spectrogram and decode with faster settings
        mel = whisper.log_mel_spectrogram(whisper_audio).to(model_m.device)
        result = whisper.decode(model_m, mel, options)
        print(f"Chunk {i // (chunk_duration * sr) + 1} transcription:", result.text)

        # Append the chunk's transcription
        transcription_result.append(result.text)

    # Combine all chunks' transcriptions into one final transcription
    full_transcription = " ".join(transcription_result)

    # Generate output file paths
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    # transcription_path = os.path.join(transcription_dir, f"{base_name}_transcription.txt")
    # translation_path = os.path.join(translation_dir, f"{base_name}_translation.txt")

    # # Save the transcription to a file
    # with open(transcription_path, "w", encoding="utf-8") as file:
    #     file.write(full_transcription)
    # print(f"Transcription saved to {transcription_path}")

    # Translate the entire audio to English
    translation_result = model_m.transcribe(file_path, language="en", fp16=False)["text"]

    # # Save the translation to a file
    # with open(translation_path, "w", encoding="utf-8") as file:
    #     file.write(translation_result)
    # print(f"Translation saved to {translation_path}")

    return translation_result

# absolute_file_path = r"C:\Users\mitta\OneDrive - iiit-b\Documents\ML-Fiesta-Byte-Synergy-Hackathon\dataset\audiocorpus\SandalWoodNewsStories_282.mp3"
# process_audio(absolute_file_path)