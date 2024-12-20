# Import necessary libraries from SpeechBrain
import torch
from speechbrain.pretrained import Tacotron2, HIFIGAN
import soundfile as sf
from django.utils import timezone

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
    # Convert text to the mel spectrogram using Tacotron2
    mel_output, mel_length, alignment = tacotron2.encode_text(text)
    
    # Convert mel spectrogram to audio waveform using HIFIGAN Vocoder
    # waveform = hifi_gan.decode_batch(mel_output)
    waveforms = hifi_gan.decode_batch(mel_output)
    
    # Save the generated waveform as a .wav file
    # waveform = waveform.squeeze(1).cpu().detach().numpy()  # Remove batch dimension and convert to NumPy array
    # write("output.wav", 22050, waveform)  # Save as output.wav with 22050 Hz sampling rate
    sf.write(f"{str(timezone.now())}.wav", waveforms.squeeze().cpu().numpy(), 22050)
    
    print("Audio saved as output.wav")

# Example usage
text = "Hello there, I am Soham from AI Pioneers in Plugin Hackathon."
text_to_speech(text)
