# Import necessary libraries from SpeechBrain
import torch
from speechbrain.pretrained import Tacotron2, HIFIGAN
import soundfile as sf

# Load the pre-trained Tacotron2 TTS model and Vocoder model (HIFIGAN)
tacotron2 = Tacotron2.from_hparams(
    source="speechbrain/tts-tacotron2-ljspeech",
    savedir="tmpdir_tts_tacotron2",
    run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"},
     # Avoid symbolic links by copying files
)

hifi_gan = HIFIGAN.from_hparams(
    source="speechbrain/tts-hifigan-ljspeech",
    savedir="tmpdir_hifigan",
    run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"},
   # Avoid symbolic links by copying files
)

# Function to convert text to speech
def text_to_speech(text: str):
    try:
        # Convert text to the mel spectrogram using Tacotron2
        mel_output, mel_length, alignment = tacotron2.encode_text(text)
        
        # Convert mel spectrogram to audio waveform using HIFIGAN Vocoder
        waveforms = hifi_gan.decode_batch(mel_output)
        
        # Generate a dynamic output filename
        import datetime
        output_filename = f"output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        # Save the generated waveform as a .wav file
        sf.write(output_filename, waveforms.squeeze().cpu().numpy(), 22050)
        
        print(f"Audio saved as {output_filename}")
    except Exception as e:
        print(f"Error occurred: {e}")

# Example usage
text = "Hello there, I am Soham from AI Pioneers in Plugin Hackathon."
text_to_speech(text)
