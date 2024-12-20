from django.shortcuts import render
from mainapp.models import User, Report, VideoAudio
from mainapp.serializers import UserSerializer, ReportSerializer, VideoAudioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpRequest
from ML_Models.speech_to_text import process_audio
import warnings
import pickle
# from ML_Models.Grammer import process_text_file
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView
)
from mainapp.serializers import CustomTokenObtainPairSerializer
import sys
import os
from gramformer import Gramformer
import re
from ML_Models.speech_to_text import process_audio

from pydub import AudioSegment
from pydub.silence import split_on_silence
import wave
import os
import json
import nltk
from nltk.tokenize import word_tokenize
from vosk import Model, KaldiRecognizer

# EXPRESSION DETECTION

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions

# Download NLTK data (only run this once)

# nltk.download('punkt')
# nltk.download('punkt_tab')

# FLUENCY

# Define filler words
filler_words = {
    "uh", "um", "er", "ah", "hmm", "you know", "actually", "basically", 
    "literally", "so", "well", "okay", "right", "I mean", "sort of", "kind of", 
    "you see", "at the end of the day", "as it were", "to be honest", 
    "truth be told", "let's see", "how do I put this", "uh huh", "yeah", 
    "I guess", "I suppose", "in a way", "if you will", "you get what I mean", 
    "you know what I mean", "you know what I’m saying", "like I said", 
    "if that makes sense", "basically speaking", "sorta kinda", "to some extent", 
    "let me think", "you know what", "honestly", "essentially", "at this point", 
    "more or less", "what I mean is", "you know right", "I would say", "by the way", 
    "in fact", "shall we say","as such"
}
model_path =r'C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\ML_Models\vosk-model-en-in-0.5'   # Path to your Vosk model
#model_path='../ML_Models/vosk-model-en-in-0.5'   # Path to your Vosk model
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

    return (speaking_rate, pause_count, filler_word_count, fluency_score)

# GRAMMAR

gf = Gramformer(models=1, use_gpu=False)

def correct_sentence_with_error_count(sentence):
    """
    Correct a sentence and count the errors.

    Args:
        gf (Gramformer): Initialized Gramformer model.
        sentence (str): Original sentence to correct.

    Returns:
        tuple: (corrected_sentence, error_count, error_details)
    """
    corrections = list(gf.correct(sentence))
    corrected_sentence = corrections[0] if corrections else sentence
    # error_count, error_details = count_errors(sentence, corrected_sentence)
    
    # return corrected_sentence, error_count, error_details
    return corrected_sentence

def process_text_file(incorrect:list[str]):
    """
    Process a text file, calculate grammar errors, and save the corrected output.

    Args:
        file_path (str): Path to the input text file.
        output_path (str): Path to save the corrected output file.

    Returns:
        dict: A dictionary with error count, total sentences, and grammar score.
    """
    # if not os.path.exists(file_path):
    #     raise FileNotFoundError(f"File '{file_path}' does not exist.")

    # with open(file_path, "r", encoding="utf-8") as file:
    #     lines = file.readlines()

    corrected_sentences = []
    total_sentences = 0
    total_errors = 0
    all_error_details = []

    # Process each sentence
    for line in incorrect:
        # Split on punctuation (periods, exclamation marks, question marks) and new lines
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\n)', line.strip())
        for sentence in sentences:
            if sentence.strip():  # Ignore empty sentences
                total_sentences += 1
                corrected= correct_sentence_with_error_count(sentence.strip())
                corrected_sentences.append(corrected)
                # total_errors += errors
                # all_error_details.extend(error_details)

    # # Save corrected sentences to output file
    # with open(output_path, "w", encoding="utf-8") as file:
    #     file.write("\n".join(corrected_sentences))

    # Return the results
    return {
        "total_sentences": total_sentences,
        "total_errors": total_errors,
        "grammar_score": total_errors,  # Number of errors as grammar score
        # "output_file": output_path,
        "error_details": all_error_details,
        "corrected_sentences": corrected_sentences
    }

# TEXT TO SPPECH

import torch
# from speechbrain.lobes.features import Tacotron2, HIFIGAN
from speechbrain.pretrained import Tacotron2, HIFIGAN
from scipy.io.wavfile import write
import soundfile as sf
from django.utils import timezone

# Load the pre-trained Tacotron2 TTS model and Vocoder model (HIFIGAN)
tacotron2 = Tacotron2.from_hparams(
    source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts_tacotron2", run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
)
hifi_gan = HIFIGAN.from_hparams(
    source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_hifigan", run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
)

# Function to convert text to speech
def text_to_speech(text: str) -> str:
    # Convert text to the mel spectrogram using Tacotron2
    mel_output, mel_length, alignment = tacotron2.encode_text(text)
    
    # Convert mel spectrogram to audio waveform using HIFIGAN Vocoder
    waveforms = hifi_gan.decode_batch(mel_output)
    
    # Generate a valid filename using the current timestamp
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    output_dir = "media/wavfiles"
    output_file = os.path.join(output_dir, f"{timestamp}.wav")
    
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the generated waveform as a .wav file
    sf.write(output_file, waveforms.squeeze().cpu().numpy(), 22050)
    
    print(f"Audio saved as {output_file}")
    return output_file

# PRONUNCIATION

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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def user_Post(request: HttpRequest) -> Response:
    """
    Request JSON body (form data):
    {
        "email": email,
        "username": username,
        "password": password
    }
    """
    if request.method == 'POST':
        data = request.data
        try:
            serializer = UserSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'error': serializer.errors
                })
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
            return Response({
                'message': 'User created successfully.'
            })
        except Exception as e:
            return Response({
                'error': e
            })
    else:
        return Response({
            'message': f'Only POST request allowed but got {request.method}.'
        })

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_Get_Delete(request: HttpRequest) -> Response:
    if request.method == 'GET':
        """
        Query parameters:
        email
        """
        email = request.GET.get('email', None)
        if email is None:
            return Response({
                'message': 'Email is None.'
            })
        try:
            user = User.objects.get(email=email)
            user_serializer = UserSerializer(user)
            return Response({
                'user': user_serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {email} does not exist.'
            })
    elif request.method == 'DELETE':
        """
        Request JSON body:
        email
        """
        email = request.data.get('email')
        if email is None:
            return Response({
                'message': 'Email is None.'
            })
        try:
            user = User.objects.get(email=email)
            user.delete()
            return Response({
                'message': 'User deleted successfully.'
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {email} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': e
            })
    else:
        return Response({
            'message': f'Allowed request methods are GET AND DELETE but got {request.method}.'
        })

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def video_audio_CRUD(request: HttpRequest) -> Response:
    if request.method == 'POST':
        """
        form data:
        {
            title,
            video_file,
            audio_file,
            user_email
        }
        """
        try:
            user = User.objects.get(email=request.POST.get('user_email'))
            video_audio = VideoAudio.objects.create(
                title=request.POST.get('title'),
                video_file=request.FILES.get('video_file'),
                audio_file=request.FILES.get('audio_file'),
                user=user
            )
            serializer = VideoAudioSerializer(video_audio)
            return Response({
                'saved': serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f"User with email = {request.POST.get('user_email')} does not exist."
            })
        except Exception as e:
            return Response({
                'error': f'{e}'
            })
    if request.method == 'GET':
        """
        It is a GET query parameter.
        id
        """
        try:
            id = request.GET.get('id')
            video_audio = VideoAudio.objects.get(id=id)
            serializer = VideoAudioSerializer(video_audio)
            return Response({
                'message': serializer.data
            })
        except VideoAudio.DoesNotExist:
            return Response({
                'message': f'Video audio with ID = {id} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': f'{e}'
            })
    if request.method == 'PUT':
        """
        raw JSON data:
        {
            title,
            video_file,
            audio_file,
            video_audio_id
        }
        """
        try:
            video_audio = VideoAudio.objects.get('video_audio_id')
            video_audio.video_file = request.FILES.get('video_file')
            video_audio.audio_file = request.FILES.get('audio_file')
            video_audio.save()
            serializer = VideoAudioSerializer(video_audio)
            return Response({
                'updated': serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with ID = {id} does not exist.'
            })
        except VideoAudio.DoesNotExist:
            return Response({
                'message': f'Video audo with ID = {id} does not exist.'
            })
        except Exception as e:
            return Response({
                'error': f'{e}'
            })
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_Analysis(request: HttpRequest) -> Response:
    """
    To get the detailed report.
    """
    if request.method == 'GET':
        """
        id: query url param
        """
        try:
            video_audio = VideoAudio.objects.get(id=request.GET.get('id'))
            user_email = request.GET.get('email')
            user = User.objects.get(email=user_email)
            text_of_speech = process_audio(video_audio.audio_file.path)
            text_of_speech_refined = text_of_speech.strip().split('.')
            print(text_of_speech_refined)
            grammar_Maal = process_text_file(text_of_speech_refined)
            fluency_tuple = analyze_audio(video_audio.audio_file.path, model_path=model_path)
            pronunciation_WAV_path = text_to_speech(text=text_of_speech)
            pronunciation_score, analysis = calculate_pronunciation_score(original_audio_path=video_audio.audio_file.path, ideal_audio_path=pronunciation_WAV_path)
            model = None
            with open(r"C:\Users\mitta\OneDrive - iiit-b\Documents\Plugin\PluginBackend\ML_Models\body_language_rf.pkl", 'rb') as f:
                model = pickle.load(f)

            # Expression Detection
            expression_analysis = {
                "Happy": 0,
                "Sad": 0,
                "Angry": 0,
                "Surprised": 0,
                "Confused": 0,
                "Tension": 0,
                "Excited": 0,
                "Pain": 0,
                "Depressed": 0
            }
            try:
                cap = cv2.VideoCapture(video_audio.video_file.path)

                emotions = []
                warnings.filterwarnings('ignore')

                # Initiate holistic model
                with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                    
                    while cap.isOpened():
                        ret, frame = cap.read()
                        
                        # Recolor Feed
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image.flags.writeable = False        
                        
                        # Make Detections
                        results = holistic.process(image)
                        # print(results.face_landmarks)
                        
                        # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks
                        
                        # Recolor image back to BGR for rendering
                        image.flags.writeable = True   
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        
                        # 1. Draw face landmarks
                        mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS, 
                                                mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                                                mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                                                )
                        
                        # 2. Right hand
                        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                                mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                                mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                                )

                        # 3. Left Hand
                        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                                mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                                mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                                )

                        # 4. Pose Detections
                        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                                )
                        # Export coordinates
                        try:
                            # Extract Pose landmarks
                            pose = results.pose_landmarks.landmark
                            pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())
                            
                            # Extract Face landmarks
                            face = results.face_landmarks.landmark
                            face_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in face]).flatten())
                            
                            # Concate rows
                            row = pose_row+face_row

                            # Make Detections
                            X = pd.DataFrame([row])
                            body_language_class = model.predict(X)[0]
                            body_language_prob = model.predict_proba(X)[0]
                            emotions.append(str(body_language_class))
                            print(body_language_class, body_language_prob)

                            expression_analysis[body_language_class.split(' ')[0]] += 1
                            
                        except Exception as e:
                            print("Exception:", e)

                cap.release()
                cv2.destroyAllWindows()
            except:
                pass

            final_Maal = {
                'grammer_Maal': grammar_Maal,
                "text_of_speech": text_of_speech,
                "speaking_rate": fluency_tuple[0],
                "pause_count": fluency_tuple[1],
                "fluency_score": fluency_tuple[2],
                "filler_word_count": fluency_tuple[3],
                "pronunciation_score": pronunciation_score,
                "pronunciation_analysis": analysis,
                "expression_analysis": expression_analysis
            }

            report = Report.objects.create(
                video_audio=video_audio,
                user=user,
                report=final_Maal
            )
            serializer = ReportSerializer(report)

            return Response({
                'report': serializer.data
            })
        
        except VideoAudio.DoesNotExist:
            return Response({
                'message': f"Video audio with ID = {request.GET.get('id')} does not exist."
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {user_email} does not exist.'
            })
    else:
        return Response({
            'message': f'Expected GET request but got {request.method}.'
        })
        
@api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_history_reports(request: HttpRequest) -> Response:
    if request.method == 'GET':
        """
        GET query url parameter:
        user_email
        """
        try:
            user = User.objects.get(email=request.GET.get('user_email'))
            reports = Report.objects.filter(user=user)
            report_serializer = ReportSerializer(reports, many=True)
            return Response({
                'reports': report_serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f"User with email = {request.GET.get('user_email')} does not exist."
            })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_Reports(request:HttpRequest) -> Response:
    if request.method == 'GET':
        email = request.GET.get('email')
        try:
            user = User.objects.get(email=email)
            reports = Report.objects.get(user=user)
            serializer = ReportSerializer(reports, many=True)
            return Response({
                'message': serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'message': f'User with email = {email} does not exist.'
            })
    else:
        return Response({
            'mesage': f'Expected request method was GET but got {request.method}.'
        })

def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>HOME</h1>")